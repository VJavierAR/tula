from odoo import _,fields, api,models
from odoo.models import TransientModel
import datetime, time
from odoo.exceptions import UserError,RedirectWarning
from odoo.tools.float_utils import float_compare
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from pdf2image import convert_from_path, convert_from_bytes
import os
import re
from PyPDF2 import PdfFileMerger, PdfFileReader,PdfFileWriter
from io import BytesIO as StringIO
import base64
import datetime
from odoo.tools.mimetypes import guess_mimetype
import logging, ast
from odoo.tools import config, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
_logger = logging.getLogger(__name__)

try:
    import xlrd
    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None

try:
    from . import odf_ods_reader
except ImportError:
    odf_ods_reader = None

FILE_TYPE_DICT = {
    'text/csv': ('csv', True, None),
    'application/vnd.ms-excel': ('xls', xlrd, 'xlrd'),
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ('xlsx', xlsx, 'xlrd >= 1.0.0'),
    'application/vnd.oasis.opendocument.spreadsheet': ('ods', odf_ods_reader, 'odfpy')
}
EXTENSIONS = {
    '.' + ext: handler
    for mime, (ext, handler, req) in FILE_TYPE_DICT.items()
}

class ReturnPickInherit(TransientModel):
    _inherit ='stock.return.picking'
    almacen=fields.Many2one('stock.warehouse')
    
    @api.onchange('almacen')
    def loc(self):
        for record in self:
            record['location_id']=record.almacen.lot_stock_id.id

class StockPickingMassAction(TransientModel):
    _name = 'stock.picking.mass.action'
    _description = 'Stock Picking Mass Action'

    @api.model
    def _default_check_availability(self):
        return self.env.context.get('check_availability', False)

    @api.model
    def _default_transfer(self):
        return self.env.context.get('transfer', False)

    def _default_picking_ids(self):
        return self.env['stock.picking'].browse(
            self.env.context.get('active_ids'))

    confirm = fields.Boolean(
        string='Mark as Todo',
        default=True,
        help="check this box if you want to mark as Todo the"
        " selected Pickings.",
    )
    check_availability = fields.Boolean(
        string='Check Availability',
        default=lambda self: self._default_check_availability(),
        help="check this box if you want to check the availability of"
        " the selected Pickings.",
    )
    transfer = fields.Boolean(
        string='Transfer',
        default=lambda self: self._default_transfer(),
        help="check this box if you want to transfer all the selected"
        " pickings.\n You'll not have the possibility to realize a"
        " partial transfer.\n If you want  to do that, please do it"
        " manually on the picking form.",
    )
    picking_ids = fields.Many2many(
        string='Pickings',
        comodel_name="stock.picking",
        default=lambda self: self._default_picking_ids(),
        help="",
    )
    check=fields.Integer(compute='che')
    tecnicos=fields.One2many('mass.tecnico','mass_id')
    evidencia=fields.Many2many('ir.attachment', string="Evidencias")

    @api.depends('picking_ids')
    def che(self):
        for s in self.picking_ids:
            #Almacen
            if(s.picking_type_id.id==3 or s.picking_type_id.id==31485 or s.picking_type_id.id==89):
                self.check=2
            #refacion
            if(s.picking_type_id.id==29314):
                self.tecnicos=[{'pick_id':s.id}]
                self.check=1
            #ruta
            if(s.picking_type_id.id==2):
                self.check=3
            #distribucion
            if(s.picking_type_id.id==29302):
                self.check=4
                
    def retiro_mass_action(self,c):
        tipo=self.picking_ids.mapped('sale_id.x_studio_tipo_de_solicitud')
        if('Retiro' in tipo):
            if(c==0):
                for pickis in self.picking_ids:
                    for move in pickis.move_ids_without_package:
                        serie=move.sale_line_id.x_studio_field_9nQhR.id
                        if(serie):
                            qu1=self.env['stock.quant'].search([['location_id','=',move.location_id.id],['product_id','=',move.product_id.id],['lot_id','=',serie]])
                            if(qu1.id==False):
                                qu1=self.env['stock.quant'].create({'location_id':move.location_id.id,'product_id':move.product_id.id,'quantity':1,'lot_id':serie})
            if(c!=0):
                for pickis in self.picking_ids:
                    for move in pickis.move_ids_without_package:
                        serie=move.sale_line_id.x_studio_field_9nQhR.id
                        if(serie):
                            d=self.env['stock.move.line'].search([['move_id','=',move.id]])
                            qu1=self.env['stock.quant'].search([['location_id','=',move.location_id.id],['product_id','=',move.product_id.id],['lot_id','=',serie]])
                            qu=self.env['stock.quant'].search([['location_id','=',move.location_id.id],['product_id','=',move.product_id.id],['lot_id','=',d.lot_id.id]])
                            self.env.cr.execute("update stock_quant set reserved_quantity=1 where id="+str(qu1.id)+";")
                            if(qu.id):            
                                self.env.cr.execute("update stock_quant set reserved_quantity=0 where id="+str(qu.id)+";")
                            if(d.id):
                                self.env.cr.execute("update stock_move_line set lot_id="+str(serie)+"where id="+str(d.id)+";")
            return True
        else:
            return True

    def mass_action(self):
        # un reserved
        # self.picking_ids.write({'surtir':True})
        # locations=self.picking_ids.mapped('picking_type_id.warehouse_id.lot_stock_id.id')
        tipo=self.picking_ids.mapped('picking_type_id.code')
        # unresrved=self.env['stock.picking'].search(['&','&','&',['id','not in',self.picking_ids.mapped('id')],['location_id','in',locations],['state','=','assigned'],['surtir','=',False]])
        # if(len(unresrved)>0 and 'outgoing' not in tipo):
        #     unresrved.do_unreserve()
        #asignacion
        # draft_picking_lst = self.picking_ids.filtered(lambda x: x.state == 'draft').sorted(key=lambda r: r.scheduled_date)
        # pickings_to_check = self.picking_ids.filtered(lambda x: x.state not in ['draft','cancel','done',]).sorted(key=lambda r: r.scheduled_date)
        # draft_picking_lst.action_confirm()
        # pickings_to_check.action_assign()
        #quantities_done = sum(move_line.qty_done for move_line in assigned_picking_lst.mapped('move_line_ids').filtered(lambda m: m.state not in ('done', 'cancel')))
        self.retiro_mass_action(0)
        assigned_picking_lst = self.surtir()
        #retiro
        self.retiro_mass_action(1)
        #reporte
        assigned_picking_lst2 = assigned_picking_lst.filtered(lambda x: self.check==1 or self.check==2)
        #concentrado
        if(self.check ==2 or self.check ==1):
            CON=str(self.env['ir.sequence'].next_by_code('concentrado'))
            self.env['stock.picking'].search([['sale_id','in',assigned_picking_lst.mapped('sale_id.id')]]).write({'concentrado':CON})
            resto=assigned_picking_lst.filtered(lambda x:x.sale_id.id==False)
            for r in resto:
                self.env['stock.picking'].search([['origin','=',r.origin]]).write({'concentrado':CON})        
        #pick_to_backorder = self.env['stock.picking']
        #pick_to_do = self.env['stock.picking']
        for picking in assigned_picking_lst:
            #for move in picking.move_lines.filtered(lambda m: m.state not in ['done', 'cancel']):
            #    for move_line in move.move_line_ids:
            #        move_line.qty_done = move_line.product_uom_qty
            #if picking._check_backorder():
            #    pick_to_backorder |= picking
            #    continue
            if(picking.sale_id.x_studio_field_bxHgp):
                if(self.check==2):
                    picking.sale_id.x_studio_field_bxHgp.write({'stage_id':94})
                    self.env['helpdesk.diagnostico'].create({ 'write_uid': self.env.user.name,'ticketRelacion' : picking.sale_id.x_studio_field_bxHgp.id, 'create_uid' : self.env.user.id,'write_uid':self.env.user.id, 'estadoTicket' : "A distribución", 'comentario':''}) 
                if(self.check==3):
                    if picking._check_backorder() and picking.sale_id.x_studio_field_bxHgp.x_studio_tipo_de_vale=='Requerimiento':
                        picking.sale_id.x_studio_field_bxHgp.write({'stage_id':109})
                        self.env['helpdesk.diagnostico'].create({'write_uid': self.env.user.name, 'ticketRelacion' : picking.sale_id.x_studio_field_bxHgp.id, 'create_uid' : self.env.user.id,'write_uid':self.env.user.id, 'estadoTicket' : "Entregado", 'comentario':picking.x_studio_comentario_1+' Evidenciado'+' Hecho por'+self.env.user.name,'evidencia':[(6,0,self.evidencia.ids)]})                        
                    if(picking.sale_id.x_studio_field_bxHgp.x_studio_tipo_de_vale!='Requerimiento') and (picking.sale_id.x_studio_field_bxHgp.stage_id.id!=18 and picking.sale_id.x_studio_field_bxHgp.stage_id.id!=4):
                        picking.sale_id.x_studio_field_bxHgp.write({'stage_id':13})
                        self.env['helpdesk.diagnostico'].create({ 'write_uid': self.env.user.name,'ticketRelacion' : picking.sale_id.x_studio_field_bxHgp.id, 'create_uid' : self.env.user.id,'write_uid':self.env.user.id, 'estadoTicket' : "Entregado", 'comentario':picking.x_studio_comentario_1 if(picking.x_studio_comentario_1) else ''+' Evidenciado'+' Hecho por'+self.env.user.name})    
                    if(picking.sale_id.x_studio_field_bxHgp.x_studio_tipo_de_vale=='Requerimiento' and picking._check_backorder()==False):
                        picking.sale_id.x_studio_field_bxHgp.write({'stage_id':18})
                        self.env['helpdesk.diagnostico'].create({ 'write_uid': self.env.user.name,'ticketRelacion' : picking.sale_id.x_studio_field_bxHgp.id, 'create_uid' : self.env.user.id,'write_uid':self.env.user.id, 'estadoTicket' : "Entregado", 'comentario':picking.x_studio_comentario_1+' Evidenciado'+' Hecho por'+self.env.user.name,'evidencia':[(6,0,self.evidencia.ids)]})    
                if(self.check==4):
                    picking.sale_id.x_studio_field_bxHgp.write({'stage_id':94})
                    self.env['helpdesk.diagnostico'].create({ 'write_uid': self.env.user.name,'ticketRelacion' : picking.sale_id.x_studio_field_bxHgp.id, 'create_uid' : self.env.user.id,'write_uid':self.env.user.id, 'estadoTicket' : "Distribución", 'comentario':''+' Hecho por'+self.env.user.name}) 
                if(self.check==1):
                    comentario=picking.x_studio_comentario_1 if(picking.x_studio_comentario_1) else 'refacion entregada'
                    if(picking.location_dest_id.id!=16):
                        ultimo=self.env['helpdesk.diagnostico'].search([['ticketRelacion','=',picking.sale_id.x_studio_field_bxHgp.id]],order='create_date desc',limit=1)
                        self.env['helpdesk.diagnostico'].create({ 'write_uid': self.env.user.name,'ticketRelacion' : picking.sale_id.x_studio_field_bxHgp.id, 'create_uid' : self.env.user.id,'write_uid':self.env.user.id, 'estadoTicket' : "Entregado", 'comentario':str(comentario)+' Evidenciado'+' Hecho por'+self.env.user.name})
                        if(picking.sale_id.x_studio_field_bxHgp.stage_id.id!=18 and picking.sale_id.x_studio_field_bxHgp.stage_id.id!=4 and picking.sale_id.x_studio_field_bxHgp.stage_id.id!=3):
                            picking.sale_id.x_studio_field_bxHgp.write({'stage_id':104})
                        else:
                            ultimo.copy()
                    else:
                        ultimo=self.env['helpdesk.diagnostico'].search([['ticketRelacion','=',picking.sale_id.x_studio_field_bxHgp.id]],order='create_date desc',limit=1)
                        self.env['helpdesk.diagnostico'].create({ 'write_uid': self.env.user.name,'ticketRelacion' : picking.sale_id.x_studio_field_bxHgp.id, 'create_uid' : self.env.user.id,'write_uid':self.env.user.id, 'estadoTicket' : "Entregado", 'comentario':str(comentario)+' Evidenciado'+' Hecho por'+self.env.user.name})    
                        if(picking.sale_id.x_studio_field_bxHgp.stage_id.id!=18 and picking.sale_id.x_studio_field_bxHgp.stage_id.id!=4 and picking.sale_id.x_studio_field_bxHgp.stage_id.id!=3):
                            picking.sale_id.x_studio_field_bxHgp.write({'stage_id':112})
                        else:
                            ultimo.copy()       
            #pick_to_do |= picking
        #if pick_to_do:
        #    pick_to_do.action_done()
        #if pick_to_backorder and assigned_picking_lst.mapped('sale_id.id')==[]:
        #    pick_to_backorder.action_done()
        #self.picking_ids.action_done()
        #mini=self.picking_ids.filtered(lambda x:x.mini==True)
        #for m in mini:
        #    backorder_pick = self.env['stock.picking'].search([('backorder_id', '=', m.id)])
        #    backorder_pick.action_cancel()
        if(len(assigned_picking_lst2)>0):
            return self.env.ref('stock_picking_mass_action.report_custom').report_action(assigned_picking_lst2)
        for pp in assigned_picking_lst.filtered(lambda x:x.sale_id.x_studio_tipo_de_solicitud!="Retiro" and x.sale_id.x_studio_field_bxHgp.id==False):
            if('incoming' not in tipo):
                if('outgoing' in tipo):
                     pp.sale_id.write({'state':'entregado'})
                else:
                    move_lines=self.env['stock.move.line'].search([['move_id','in',pp.mapped('move_lines.id')]])
                    tipo2=move_lines.mapped('move_id.picking_type_id.name')
                    if('Distribución' in tipo2):
                        pp.sale_id.write({'state':'distribucion'})
    @api.multi
    def surtir(self):
        self.ensure_one()
        # un reserved
        self.picking_ids.write({'surtir':True})
        almacenes=self.env['stock.warehouse'].search([['x_studio_cliente','=',False]]).mapped('lot_stock_id.id')
        locations=self.picking_ids.mapped('location_id.id')
        tipo=self.picking_ids.mapped('picking_type_id.code')
        if(locations[0] in almacenes):
            unresrved=self.env['stock.picking'].search(['&','&','&',['id','not in',self.picking_ids.mapped('id')],['location_id','in',locations],['state','=','assigned'],['surtir','=',False],['oculta','=',False]])
            if(len(unresrved)>0 and 'outgoing' not in tipo):
                _logger.info('entre en anular reserva')
                unresrved.do_unreserve()

        draft_picking_lst = self.picking_ids.filtered(lambda x: x.state == 'draft').sorted(key=lambda r: r.scheduled_date)
        draft_picking_lst.action_confirm()
        pickings_to_check = self.picking_ids.filtered(lambda x: x.state not in ['draft','cancel','done',]).sorted(key=lambda r: r.scheduled_date)
        pickings_to_check.action_assign()
        assigned_picking_lst = self.picking_ids.filtered(lambda x: x.state == 'assigned').sorted(key=lambda r: r.scheduled_date)
        quantities_done = sum(move_line.qty_done for move_line in assigned_picking_lst.mapped('move_line_ids').filtered(lambda m: m.state not in ('done', 'cancel')))
        #self.retiro_mass_action()
        if not quantities_done:
            q=self.env['stock.immediate.transfer'].create({'pick_ids':[(6,0,assigned_picking_lst.mapped('id'))]})
            q.process()
        if any([pick._check_backorder() for pick in assigned_picking_lst]):
            mini=assigned_picking_lst.filtered(lambda x:x.mini==True)
            nomini=assigned_picking_lst.filtered(lambda x:x.mini==False)
            b=self.env['stock.backorder.confirmation'].create({'pick_ids':[(6,0,nomini.mapped('id'))]})
            b.process()
            c=self.env['stock.backorder.confirmation'].create({'pick_ids':[(6,0,mini.mapped('id'))]})
            c.process_cancel_backorder()
        assigned_picking_lst.action_done()
        return assigned_picking_lst

    @api.multi
    def vales(self):
        assigned_picking_lst2 = self.picking_ids.\
        filtered(lambda x: (x.picking_type_id.id == 3 or x.picking_type_id.id == 29314 or x.picking_type_id.id == 89) and x.state == 'done')
        if(assigned_picking_lst2.mapped('sale_id.id')==[]):
            return self.env.ref('stock.action_report_picking').report_action(assigned_picking_lst2)
        else:
            return self.env.ref('studio_customization.vale_de_entrega_56cdb2f0-51e3-447e-8a67-6e5c7a6b3af9').report_action(assigned_picking_lst2)      
    @api.multi
    def etiquetas(self):
        assigned_picking_lst2 = self.picking_ids.\
        filtered(lambda x: (x.picking_type_id.id == 3 or x.picking_type_id.id == 29314) and x.state == 'done')
        return self.env.ref('studio_customization.transferir_reporte_4541ad13-9ccb-4a0f-9758-822064db7c9a').report_action(assigned_picking_lst2)
class MassActionTecnico(TransientModel):
    _name='mass.tecnico'
    _description='Listado para tecnicos'
    mass_id=fields.Many2one('stock.picking.mass.action',store=True)
    pick_id=fields.Many2one('stock.picking',store=True)
    tecnico=fields.Many2one('hr.employee',store=True)
    origin=fields.Char(related='pick_id.origin')
    partner_id=fields.Many2one(related='pick_id.partner_id')
    scheduled_date=fields.Datetime(related='pick_id.scheduled_date')
    x_studio_toneres=fields.Char(related='pick_id.x_studio_toneres')

    @api.depends('tecnico')
    def escribeTecnico(self):
       for record in self:
           if(record.tecnico):
               record.pick_id.write({'x_studio_tecnico':record.tecnico.id})



class StockIngreso(TransientModel):
    _name='ingreso.almacen'
    _description='Ingreso Almacen'
    pick=fields.Many2one('stock.picking')
    move_line=fields.One2many('ingreso.lines','rel_ingreso')
    almacen=fields.Many2one('stock.warehouse','Almacen')

    def confirmar(self):
        self.pick.write({'location_dest_id':self.almacen.lot_stock_id.id})
        for m in self.move_line:
            m.write({'location_dest_id':self.almacen.lot_stock_id.id})
            l=self.env['stock.move.line'].search([['move_id','=',m.move.id]])
            l.write({'location_dest_id':self.almacen.lot_stock_id.id,'qty_done':m.cantidad})
            if(m.producto.id!=m.producto2.id):
                l.write({'state':'draft'})
                l.write({'product_id':m.producto2.id})
                l.write({'state':'assigned'})
        self.pick.purchase_id.write({'recibido':'recibido'})
        self.pick.action_done()
        if(self.pick.mini):
            backorder_pick = self.env['stock.picking'].search([('backorder_id', '=', self.pick.id)])
            backorder_pick.action_cancel()
        return self.env.ref('stock.action_report_picking').report_action(self.pick)

class StockIngresoLines(TransientModel):
    _name='ingreso.lines'
    _description='lineas de ingreso'
    rel_ingreso=fields.Many2one('ingreso.almacen')
    producto=fields.Many2one('product.product')
    producto2=fields.Many2one('product.product')
    cantidad=fields.Integer()
    move=fields.Many2one('stock.move')    



class StockCambio(TransientModel):
    _name = 'cambio.toner'
    _description = 'Cambio toner'
    pick=fields.Many2one('stock.picking')
    pro_ids = fields.One2many('cambio.toner.line','rel_cambio')
    tonerUorden=fields.Boolean()
    toner_ids = fields.One2many('cambio.toner.line.toner','rel_cambio')
    accesorios_ids = fields.One2many('cambio.toner.line.accesorios','rel_cambio')



    def otra(self):
        equipos=self.pro_ids.filtered(lambda x:x.producto1.categ_id.id==13)
        if(len(equipos)==0 or self.pick.picking_type_id.id==29314):
            self.confirmar(self.pro_ids)
        else:   
            self.confirmar(self.accesorios_ids)
            self.confirmar(self.toner_ids)
            self.valida(equipos)
            self.confirmar(equipos)
            self.confirmarE(equipos)
            wiz=self.env['lot.assign.accesorios'].create({'pick':self.pick.id,'domain':str(self.accesorios_ids.mapped('producto2.id'))})
            for e in equipos:
                wizline=self.env['lot.assign.accesorios.lines'].create({'lot_id':e.serieOrigen.id,'rel_id':wiz.id})            
            view = self.env.ref('stock_picking_mass_action.view_lot_assign_accesorios')
            if(len(self.accesorios_ids)!=0):
                return {
                    'name': _('Accesorios'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'lot.assign.accesorios',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target': 'new',
                    'res_id': wiz.id,
                    'context': self.env.context,
                }                
            else:
                wiz=self.env['stock.picking.mass.action'].create({'picking_ids':[(4,self.pick.id)],'confirm':True,'check_availability':True,'transfer':True})
                view = self.env.ref('stock_picking_mass_action.view_stock_picking_mass_action_form')
                return {
                    'name': _('Transferencia'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'stock.picking.mass.action',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target': 'new',
                    'res_id': wiz.id,
                    'context': self.env.context,
                }


    def confirmar(self,data):
        if(self.pick.sale_id):
            i=0
            self.pick.backorder=''
            orden=self.env['sale.order'].browse(self.pick.sale_id.id)
            lenOrderLine=len(orden.order_line)
            dt=[]
            al=[]
            cantidades=False
            productos=False
            ubicacion=False
            temp=[]
            almacenes=self.env['stock.warehouse'].search([['x_studio_cliente','=',False]])
            ruta=orden.mapped('order_line.route_id.id')
            pic=self.env['stock.picking'].search(['&',['location_id','in',almacenes.mapped('lot_stock_id.id')],['sale_id','=',orden.id]],order='id asc',limit=1)
            for d in data:
                if(d.producto1.id!=d.producto2.id):
                    productos=True
                if(d.cantidad!=d.cantidad2):
                    cantidades=True
                if(d.almacen.id):
                    ubicacion=True
            if(productos or cantidades):
                self.pick.do_unreserve()
                for d in data:
                    ssss=self.env['stock.move'].search([['sale_line_id','=',d.move_id.sale_line_id.id],['state','!=','done'],['picking_id','in',self.pick.sale_id.mapped('picking_ids.id')]])
                    ssss.write({'product_id':d.producto2.id})
                    if(ubicacion):
                        temp.append({'sale_line_id':d.move_id.sale_line_id.id,'product_id':d.producto2.id,'location_id':d.almacen.lot_stock_id.id})
            if(ubicacion and (productos or cantidades)):
                check=False
                for t in temp:
                    dd=self.env['stock.move'].search(['&',['sale_line_id','=',t['sale_line_id']],['location_id','in',almacenes.mapped('lot_stock_id.id')]],order='id asc',limit=1)
                    if(dd.location_id.id!=t['location_id']):
                        dd.write({'location_id':t['location_id']})
                        check=True
            if(ubicacion and not(productos or cantidades)):
                self.pick.do_unreserve()
                for d in data:
                    if(d.almacen.id):
                        d.move_id.write({'location_id':d.almacen.lot_stock_id.id})
            self.pick.action_assign()
            if(cantidades):
                for d in data:
                    _logger.info(len(d.move_id.move_line_ids))
                    #ssss=self.env['stock.move'].search([['sale_line_id','=',d.move_id.sale_line_id.id],['state','!=','done'],['picking_id','in',self.pick.sale_id.mapped('picking_ids.id')]])    
                    #if(cantidades==True):    
                    #    ssss.write({'product_id':d.producto2.id})
                    if(d.existeciaAlmacen):
                        self.env['stock.move.line'].search([['move_id','=',d.move_id.id]]).write({'qty_done':0})
                    if(d.cantidad2>d.cantidad):
                        self.env['stock.move.line'].search([['move_id','=',d.move_id.id]]).write({'qty_done':d.cantidad})
                    else:
                        self.env['stock.move.line'].search([['move_id','=',d.move_id.id]]).write({'qty_done':d.cantidad2})


    def valida(self,equipos):
        for s in equipos:
            qu1=self.env['stock.quant'].search([['location_id','=',s.move_id.location_id.id],['product_id','=',s.move_id.product_id.id],['lot_id','=',s.serieOrigen.id]])
            if(qu1.id==False):
                qu1=self.env['stock.quant'].create({'location_id':s.almacen.lot_stock_id.id,'product_id':s.serieOrigen.product_id.id,'quantity':1,'lot_id':s.serieOrigen.id})

    def confirmarE(self,equipos):
        fecha=datetime.datetime.now()-datetime.timedelta(hours=-5)
        f="<table class='table table-sm'><thead><tr><th>Modelo</th><th>Serie</th></thead><tbody>"
        if(len(equipos.mapped('serieOrigen.id'))<len(equipos)):
            raise UserError(_('Faltan series o hay duplicidad'))  
        else:
            for s in equipos:
                d=self.env['stock.move.line'].search([['move_id','=',s.move_id.id]])
                qu1=self.env['stock.quant'].search([['location_id','=',s.move_id.location_id.id],['product_id','=',s.move_id.product_id.id],['lot_id','=',s.serieOrigen.id]])
                qu=self.env['stock.quant'].search([['location_id','=',s.move_id.location_id.id],['product_id','=',s.move_id.product_id.id],['lot_id','=',d.lot_id.id]])
                if(d.lot_id.id!=s.serieOrigen.id):
                    if(qu1.id==False):
                        qu1=self.env['stock.quant'].create({'location_id':s.almacen.lot_stock_id.id,'product_id':s.serieOrigen.product_id.id,'quantity':1,'lot_id':s.serieOrigen.id})
                    self.env.cr.execute("update stock_quant set reserved_quantity=1 where id="+str(qu1.id)+";")
                    if(qu.id):
                        self.env.cr.execute("update stock_quant set reserved_quantity=0 where id="+str(qu.id)+";")
                    self.env.cr.execute("update stock_move_line set lot_id="+str(s.serieOrigen.id)+"where id="+str(d.id)+";")            
                s.move_id.sale_line_id.write({'x_studio_field_9nQhR':s.serieOrigen.id})
                if(self.pick.sale_id.x_studio_tipo_de_solicitud=='Retiro'):
                    s.serieOrigen.write({'x_studio_demo':False,'servicio':False,'x_studio_cliente':1,'x_studio_localidad_2':self.pick.sale_id.warehouse_id.x_studio_field_E0H1Z.id})
                    self.env['cliente.h'].create({'localidad':self.pick.sale_id.partner_shipping_id.id,'solicitud':self.pick.sale_id.id,'contrato':self.pick.sale_id.x_studio_field_LVAj5.id,'servicio':self.pick.sale_id.x_studio_field_69Boh.id,'origen':self.pick.sale_id.partner_shipping_id.name,'destino':self.pick.sale_id.warehouse_id.name,'fecha':fecha,'serie':s.serieOrigen.id})
                if(self.pick.sale_id.x_studio_tipo_de_solicitud=='Backup'):
                    s.serieOrigen.write({'x_studio_demo':False,'x_studio_estado':'Back-up','servicio':self.pick.sale_id.x_studio_field_69Boh.id,'x_studio_cliente':self.pick.sale_id.partner_id.id,'x_studio_localidad_2':self.pick.sale_id.partner_shipping_id.id})
                    self.env['cliente.h'].create({'localidad':self.pick.sale_id.partner_shipping_id.id,'solicitud':self.pick.sale_id.id,'contrato':self.pick.sale_id.x_studio_field_LVAj5.id,'servicio':self.pick.sale_id.x_studio_field_69Boh.id,'origen':self.pick.sale_id.warehouse_id.name,'destino':self.pick.sale_id.partner_shipping_id.name,'fecha':fecha,'serie':s.serieOrigen.id})
                if(self.pick.sale_id.x_studio_tipo_de_solicitud=='Venta' or self.pick.sale_id.x_studio_tipo_de_solicitud=="Venta directa"):
                    s.serieOrigen.write({'x_studio_demo':False,'x_studio_venta':True,'servicio':self.pick.sale_id.x_studio_field_69Boh.id,'x_studio_cliente':self.pick.sale_id.partner_id.id,'x_studio_localidad_2':self.pick.sale_id.partner_shipping_id.id})
                    self.env['cliente.h'].create({'localidad':self.pick.sale_id.partner_shipping_id.id,'solicitud':self.pick.sale_id.id,'contrato':self.pick.sale_id.x_studio_field_LVAj5.id,'servicio':self.pick.sale_id.x_studio_field_69Boh.id,'origen':self.pick.sale_id.warehouse_id.name,'destino':self.pick.sale_id.partner_shipping_id.name,'fecha':fecha,'serie':s.serieOrigen.id})                    
                if(self.pick.sale_id.x_studio_tipo_de_solicitud=='Demostración'):
                    s.serieOrigen.write({'x_studio_demo':True,'x_studio_estado':'','servicio':self.pick.sale_id.x_studio_field_69Boh.id,'x_studio_cliente':self.pick.sale_id.partner_id.id,'x_studio_localidad_2':self.pick.sale_id.partner_shipping_id.id})
                    self.env['cliente.h'].create({'localidad':self.pick.sale_id.partner_shipping_id.id,'solicitud':self.pick.sale_id.id,'contrato':self.pick.sale_id.x_studio_field_LVAj5.id,'servicio':self.pick.sale_id.x_studio_field_69Boh.id,'origen':self.pick.sale_id.warehouse_id.name,'destino':self.pick.sale_id.partner_shipping_id.name,'fecha':fecha,'serie':s.serieOrigen.id})
                else:
                    s.serieOrigen.write({'x_studio_demo':False,'servicio':self.pick.sale_id.x_studio_field_69Boh.id,'x_studio_cliente':self.pick.sale_id.partner_id.id,'x_studio_localidad_2':self.pick.sale_id.partner_shipping_id.id})
                    self.env['cliente.h'].create({'localidad':self.pick.sale_id.partner_shipping_id.id,'solicitud':self.pick.sale_id.id,'contrato':self.pick.sale_id.x_studio_field_LVAj5.id,'servicio':self.pick.sale_id.x_studio_field_69Boh.id,'origen':self.pick.sale_id.warehouse_id.name,'destino':self.pick.sale_id.partner_shipping_id.name,'fecha':fecha,'serie':s.serieOrigen.id})
                f=f+"<tr>"
                f=f+"<td>"+str(s.serieOrigen.product_id.name)+"</td>"
                f=f+"<td>"+str(s.serieOrigen.name)+"</td>"
                f=f+"</tr>"
                da={'porcentajeNegro':s.nivelNegro,'porcentajeAmarillo':s.nivelAmarillo,'porcentajeCian':s.nivelCian,'porcentajeMagenta':s.nivelMagenta,'contadorColor':s.contadorColor,'x_studio_toner_negro':1,'x_studio_toner_amarillo':1,'x_studio_toner_cian':1,'x_studio_toner_magenta':1,'contadorMono':s.contadorMono,'serie':s.serieOrigen.id,'fuente':'stock.production.lot'}
                c=self.env['dcas.dcas'].create(da)
                a=c.copy()
                b=c.copy()
                d=c.copy()
                a.write({'fuente':'dcas.dcas'})
                b.write({'fuente':'helpdesk.ticket'})
                d.write({'fuente':'tfs.tfs'})
                #da['fuente']='dcas.dcas'
                #self.env['dcas.dcas'].create(da)
                #da['fuente']='helpdesk.ticket'
                #self.env['dcas.dcas'].create(da)
                #da['fuente']='tfs.tfs'
                #self.env['dcas.dcas'].create(da)
        f=f+"</tbody></table>"
        if(self.pick.sale_id.x_studio_tipo_de_solicitud in ['Arrendamiento','Venta','Backup']):
            self.pick.sale_id.write({'x_studio_series_retiro':f,'state':'assign'})
        else:
            self.pick.sale_id.write({'state':'assign'})





class StockCambioLine(TransientModel):
    _name = 'cambio.toner.line'
    _description = 'Lineas cambio toner'

    producto1=fields.Many2one('product.product')
    producto2=fields.Many2one('product.product',default=lambda self: self.te())
    cantidad=fields.Float()
    cantidad2=fields.Float()
    rel_cambio=fields.Many2one('cambio.toner')
    serie=fields.Many2one('stock.production.lot')
    almacen=fields.Many2one('stock.warehouse',string='Almacen')
    existeciaAlmacen=fields.Integer(string='Existencia de Almacen seleccionado',compute='almac',readonly=False)
    tipo=fields.Integer()
    serieOrigen=fields.Many2one('stock.production.lot',domain="[('product_id.id','=',producto1)]")
    estado=fields.Selection([["Obsoleto","Obsoleto"],["Usado","Usado"],["Hueso","Hueso"],["Para reparación","Para reparación"],["Nuevo","Nuevo"],["Buenas condiciones","Buenas condiciones"],["Excelentes condiciones","Excelentes condiciones"],["Back-up","Back-up"],["Dañado","Dañado"]])
    color=fields.Selection(related='producto1.x_studio_color_bn')
    contadorMono=fields.Integer('Contador Monocromatico')
    contadorColor=fields.Integer('Contador Color')
    move_id=fields.Many2one('stock.move')
    categoria=fields.Integer(related='producto1.categ_id.id')
    nivelNegro=fields.Float()
    nivelCian=fields.Float()
    nivelAmarillo=fields.Float()
    nivelMagenta=fields.Float()
    compatibilidad=fields.Boolean()

    
    @api.depends('almacen','producto2')
    def almac(self):
        res={}
        for record in self:
            if(record.almacen):
                ex=self.env['stock.quant'].search([['location_id','=',record.almacen.lot_stock_id.id],['product_id','=',record.producto2.id]]).sorted(key='quantity',reverse=True)
                record.existeciaAlmacen=int(ex[0].quantity) if(len(ex)>0) else 0


    @api.onchange('compatibilidad')
    def te(self):
        res={}
        for record in self:
            if(record.producto1.categ_id.id!=5):
                q=self.env['stock.quant'].search([['product_id.categ_id.id','=',record.producto1.categ_id.id],['quantity','>',0],['location_id','in',(35204,67,12,41917)]])
                res['domain']={'producto2':[['categ_id','=',record.producto1.categ_id.id],['id','in',q.mapped('product_id.id')]]}
                #res['domain']={'producto2':[['categ_id','=',record.producto1.categ_id.id]]}
            if(record.producto1.categ_id.id==5):
                p=self.env['product.product'].search([['categ_id','=',5],['name','ilike',record.producto1.name]])
                res['domain']={'producto2':[['id','in',p.mapped('id')]]}
        return res

class StockCambioLine(TransientModel):
    _name = 'cambio.toner.line.toner'
    _description = 'Lineas cambio toner'
    producto1=fields.Many2one('product.product')
    producto2=fields.Many2one('product.product')
    cantidad=fields.Float()
    cantidad2=fields.Float()
    rel_cambio=fields.Many2one('cambio.toner')
    serie=fields.Many2one('stock.production.lot')
    almacen=fields.Many2one('stock.warehouse',string='Almacen')
    existencia1=fields.Integer(string='Existencia Nuevo')
    existencia2=fields.Integer(string='Existencia Usado')
    existeciaAlmacen=fields.Integer(string='Existencia de Almacen seleccionado',compute='almac')
    tipo=fields.Integer()
    move_id=fields.Many2one('stock.move')

    @api.depends('almacen','producto2')
    def almac(self):
        res={}
        for record in self:
            if(record.almacen):
                ex=self.env['stock.quant'].search([['location_id','=',record.almacen.lot_stock_id.id],['product_id','=',record.producto2.id]]).sorted(key='quantity',reverse=True)
                record.existeciaAlmacen=int(ex[0].quantity) if(len(ex)>0) else 0


    @api.onchange('compatibilidad')
    def te(self):
        res={}
        for record in self:
            if(record.producto1.categ_id.id!=5):
                q=self.env['stock.quant'].search([['product_id.categ_id.id','=',record.producto1.categ_id.id],['quantity','>',0],['location_id','in',(35204,67,12,41917)]])
                res['domain']={'producto2':[['categ_id','=',record.producto1.categ_id.id],['id','in',q.mapped('product_id.id')]]}
                #res['domain']={'producto2':[['categ_id','=',record.producto1.categ_id.id]]}
            if(record.producto1.categ_id.id==5):
                p=self.env['product.product'].search([['categ_id','=',5],['name','ilike',record.producto1.name]])
                res['domain']={'producto2':[['id','in',p.mapped('id')]]}
        return res
    # @api.onchange('almacen','producto2')
    # def almac(self):
    #     res={}
    #     for record in self:
    #         if(record.almacen):
    #             ex=self.env['stock.quant'].search([['location_id','=',record.almacen.lot_stock_id.id],['product_id','=',record.producto1.id]]).sorted(key='quantity',reverse=True)
    #             record.existeciaAlmacen=int(ex[0].quantity) if(len(ex)>0) else 0
    #         if(record.producto1.categ_id.id!=5):
    #             res['domain']={'producto2':[['categ_id','=',record.producto1.categ_id.id]]}
    #         if(record.producto1.categ_id.id==5):
    #             p=self.env['product.product'].search([['categ_id','=',5],['name','ilike',record.producto1.name]])
    #             res['domain']={'producto2':[['id','in',p.mapped('id')]]}
    #     return res

class StockCambioLine(TransientModel):
    _name = 'cambio.toner.line.accesorios'
    _description = 'Lineas cambio toner'
    producto1=fields.Many2one('product.product')
    producto2=fields.Many2one('product.product')
    cantidad=fields.Float()
    cantidad2=fields.Float()
    rel_cambio=fields.Many2one('cambio.toner')
    serie=fields.Many2one('stock.production.lot')
    almacen=fields.Many2one('stock.warehouse',string='Almacen')
    existencia1=fields.Integer(string='Existencia Nuevo')
    existencia2=fields.Integer(string='Existencia Usado')
    existeciaAlmacen=fields.Integer(string='Existencia de Almacen seleccionado',compute='almac')
    tipo=fields.Integer()
    move_id=fields.Many2one('stock.move')
    
    @api.depends('almacen','producto2')
    def almac(self):
        res={}
        for record in self:
            if(record.almacen):
                ex=self.env['stock.quant'].search([['location_id','=',record.almacen.lot_stock_id.id],['product_id','=',record.producto2.id]]).sorted(key='quantity',reverse=True)
                record.existeciaAlmacen=int(ex[0].quantity) if(len(ex)>0) else 0


    @api.onchange('compatibilidad')
    def te(self):
        res={}
        for record in self:
            if(record.producto1.categ_id.id!=5):
                res['domain']={'producto2':[['categ_id','=',record.producto1.categ_id.id]]}
            if(record.producto1.categ_id.id==5):
                p=self.env['product.product'].search([['categ_id','=',5],['name','ilike',record.producto1.name]])
                res['domain']={'producto2':[['id','in',p.mapped('id')]]}
        return res
    # @api.onchange('almacen','producto2')
    # def almac(self):
    #     res={}
    #     for record in self:
    #         if(record.almacen):
    #             ex=self.env['stock.quant'].search([['location_id','=',record.almacen.lot_stock_id.id],['product_id','=',record.producto1.id]]).sorted(key='quantity',reverse=True)
    #             record.existeciaAlmacen=int(ex[0].quantity) if(len(ex)>0) else 0
    #         if(record.producto1.categ_id.id!=5):
    #             res['domain']={'producto2':[['categ_id','=',record.producto1.categ_id.id]]}
    #         if(record.producto1.categ_id.id==5):
    #             p=self.env['product.product'].search([['categ_id','=',5],['name','ilike',record.producto1.name]])
    #             res['domain']={'producto2':[['id','in',p.mapped('id')]]}
    #     return res


class GuiaTicket(TransientModel):
    _name = 'guia.ticket'
    _description = 'Guias de Ticket'
    guia=fields.Char(string='Guia')
    pick=fields.Many2one('stock.picking')

    def confirmar(self):
        if(self.guia):
            self.pick.write({'carrier_tracking_ref':self.guia})
            if(self.pick.sale_id.x_studio_field_bxHgp):
                self.pick.sale_id.x_studio_field_bxHgp.sudo().write({'x_studio_nmero_de_guia_1': self.guia})
                self.env['helpdesk.diagnostico'].sudo().create({ 'write_uid': self.env.user.name,'ticketRelacion' : self.pick.sale_id.x_studio_field_bxHgp.id, 'create_uid' : self.env.user.id, 'estadoTicket' : "Guia Agregada", 'comentario':"Guia: "+self.guia}) 



class ComemtarioTicket(TransientModel):
    _name = 'comentario.ticket'
    _description = 'Comemtario de Ticket'
    comentario=fields.Char(string='Comentario')
    evidencia=fields.Many2many('ir.attachment', string="Evidencias")
    pick=fields.Many2one('stock.picking')
    ruta=fields.Integer(related='pick.ruta_id.id')

    def confirmar(self):
        if(5>len(self.comentario)):
            raise UserError(_("Ingresar un comentario más extenso"))
        if(self.ruta==False):
            self.pick.x_studio_evidencia_a_ticket=self.evidencia
            self.pick.x_studio_comentario_1=self.comentario
            if(self.pick.sale_id.x_studio_field_bxHgp.stage_id.id==18):
                ultimo=self.env['helpdesk.diagnostico'].search([['ticketRelacion','=',self.pick.sale_id.x_studio_field_bxHgp.id]],order='create_date desc',limit=1)
                self.env['helpdesk.diagnostico'].sudo().create({'write_uid': self.env.user.name, 'ticketRelacion' : self.pick.sale_id.x_studio_field_bxHgp.id, 'create_uid' : self.env.user.id, 'write_uid' : self.env.user.id, 'estadoTicket' : "", 'comentario':self.comentario})
                ultimo.copy()
            else:
                self.env['helpdesk.diagnostico'].sudo().create({ 'write_uid': self.env.user.name,'ticketRelacion' : self.pick.sale_id.x_studio_field_bxHgp.id, 'create_uid' : self.env.user.id, 'write_uid' : self.env.user.id, 'estadoTicket' : "", 'comentario':self.comentario})
        if(self.ruta!=False and self.pick.sale_id.id!=False):
            self.pick.x_studio_evidencia_a_ticket=self.evidencia
            self.pick.x_studio_comentario_1=self.comentario
            
            #self.env['helpdesk.diagnostico'].create({'write_uid': self.env.user.name,'ticketRelacion': self.pick.sale_id.x_studio_field_bxHgp.id
                                        #,'comentario': self.comentario
                                        #,'estadoTicket': self.pick.sale_id.x_studio_field_bxHgp.stage_id.name
                                        #,'evidencia': [(6,0,self.evidencia.ids)]
                                        #,'mostrarComentario': False
                                        #})
            if(len(self.evidencia)==0 and self.pick.ruta_id.tipo!="foraneo"):
                raise UserError(_("Falta evidencia"))
            else:
                wiz=self.env['stock.picking.mass.action'].create({'picking_ids':[(4,self.pick.id)],'evidencia':[(6,0,self.evidencia.ids)],'confirm':True,'check_availability':True,'transfer':True})
                wiz.mass_action()
        if(self.ruta!=False and self.pick.sale_id.id==False):
            if(len(self.evidencia)==0 and self.pick.ruta_id.tipo!="foraneo"):
                raise UserError(_("Falta evidencia"))
            else:
                wiz=self.env['stock.picking.mass.action'].create({'picking_ids':[(4,self.pick.id)],'confirm':True,'check_availability':True,'transfer':True})
                wiz.mass_action()


class TransferInter(TransientModel):
    _name='transferencia.interna'
    _description='Transferencia Interna'    
    almacenPadre=fields.Many2one('stock.warehouse','Almacen Padre')
    almacenOrigen=fields.Many2one('stock.warehouse','Almacen Hijo',domain="[('x_studio_almacn_padre','=',almacenPadre)]")
    ubicacion=fields.Many2one(related='almacenOrigen.lot_stock_id')
    almacenDestino=fields.Many2one('stock.warehouse','Almacen Destino')
    lines=fields.One2many('transferencia.interna.temp','transfer')
    categoria=fields.Many2one('product.category','Categoria de productos')
    archivo=fields.Binary()
    
    @api.onchange('archivo')
    def agregarLineas(self):
        if(self.archivo):
            f2=base64.b64decode(self.archivo)
            H=StringIO(f2)
            mimetype = guess_mimetype(f2 or b'')
            if(mimetype=='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'):
                book = xlrd.open_workbook(file_contents=f2 or b'')
                sheet = book.sheet_by_index(0)
                header=[]
                arr=[]
                i=0
                for row_num, row in enumerate(sheet.get_rows()):
                    if(i>0):
                        code=str(row[1].value).split('0',1)[0].replace('.0','') if(str(row[1].value)[0]=='0') else str(row[1].value).replace('.0','')
                        p=self.env['product.product'].search([['default_code','=',code]])
                        self.lines=[{'producto':p.id,'cantidad':int(row[2].value)}]
                    i=i+1  
                # for ori in pickOrigen:
                #     ticket.x_studio_productos=[(4,ori['product_id'])]
                #     sl=self.env['sale.order.line'].create({'order_id' : sale.id,'product_id':ori['product_id'],'product_uom_qty':ori['product_uom_qty'], 'price_unit': 0})
                # for des in pickDestino:
                #     des['date_planned']=datetime.datetime.now()
                #     des['order_id']=compra.id
                #     self.env['purchase.order.line'].create(des)

    def confirmar(self):
        pick_dest=[]
        pick_origin=[]
        pick_origin1=[]
        pick_origin2=[]
        pick_origin3=[]
        compra=None
        orden=None
        #cliente=self.env['res.partner'].search([['name','=',self.almacenDestino.name],['parent_id','=',1]])
        cliente=self.almacenDestino.x_studio_field_E0H1Z
        if(self.almacenOrigen.id==False):
            self.almacenOrigen=self.almacenPadre.id
        if(self.almacenDestino.x_studio_almacn_padre):
            if('Foraneo' in self.almacenDestino.x_studio_almacn_padre.name):
                destino=self.env['stock.picking.type'].search([['name','=','Receipts'],['warehouse_id','=',self.almacenDestino.id]])
                orden=self.env['sale.order'].create({'partner_id':cliente.id,'partner_shipping_id':cliente.id})
                compra=self.env['purchase.order'].create({'picking_type_id':destino.id,'partner_id' : 1, 'origin' :orden.name, 'warehouse_id' :self.almacenDestino.id , 'date_planned': datetime.datetime.now(),'name':'MINI'})
                origen1=None
        else:    
            origen=self.env['stock.picking.type'].search([['name','=','Internal Transfers'],['warehouse_id','=',self.almacenOrigen.id]])
            destino=self.env['stock.picking.type'].search([['name','=','Internal Transfers'],['warehouse_id','=',self.almacenDestino.id]])
            pick_origin = self.env['stock.picking'].create({'internas':True,'picking_type_id' : origen.id,'almacenOrigen':self.almacenOrigen.id,'almacenDestino':self.almacenDestino.id,'location_id':self.almacenOrigen.lot_stock_id.id,'location_dest_id':17})
            pick_dest = self.env['stock.picking'].create({'internas':True,'picking_type_id' : destino.id, 'location_id':17,'almacenOrigen':self.almacenOrigen.id,'almacenDestino':self.almacenDestino.id,'location_dest_id':self.almacenDestino.lot_stock_id.id})
        v=0
        e=[]
        e1=[]
        for l in self.lines:
            datos1={'product_id' : l.producto.id, 'product_uom_qty' : l.cantidad,'name':l.producto.description if(l.producto.description) else '/','product_uom':l.unidad.id,'location_id':self.almacenOrigen.lot_stock_id.id,'location_dest_id':17}
            datos2={'product_id' : l.producto.id, 'product_uom_qty' : l.cantidad,'name':l.producto.description if(l.producto.description) else '/','product_uom':l.unidad.id,'location_id':17,'location_dest_id':self.almacenDestino.lot_stock_id.id}
            if(self.almacenDestino.x_studio_almacn_padre):
                if('Foraneo' in self.almacenDestino.x_studio_almacn_padre.name):
                    sl=self.env['sale.order.line'].create({'order_id' : orden.id,'name':l.producto.description if(l.producto.description) else '/','product_id':l.producto.id,'product_uom_qty':l.cantidad, 'price_unit': 0,'product_uom':l.unidad.id})
                    datos2={'product_id' : l.producto.id, 'product_qty' : l.cantidad,'name':l.producto.description if(l.producto.description) else '/','product_uom':l.unidad.id,'price_unit': 0}
                    datos2['date_planned']=datetime.datetime.now()
                    datos2['order_id']=compra.id
                    self.env['purchase.order.line'].create(datos2)
            else:
                datos1['picking_id']= pick_origin.id
                datos2['picking_id']= pick_dest.id
                a=self.env['stock.move'].create(datos1)
                b=self.env['stock.move'].create(datos2)
                pick_origin.action_confirm()
                pick_origin.action_assign()
                pick_dest.action_confirm()
                pick_dest.action_assign()
                pick_origin.action_confirm()
                pick_origin.action_assign()
                pick_dest.action_confirm()
                pick_dest.action_assign()
            if(l.producto.categ_id.id==13):
                v=1
                e.append(a.id)
                e1.append(b.id)
        if('Foraneo' in self.almacenDestino.x_studio_almacn_padre.name):
            orden.action_confirm()
            compra.button_confirm()
            compra.write({'active':False})
            pick_or=orden.picking_ids.sorted(key='id')
            pick_origin=pick_or[0]
            datP=self.env['stock.picking'].search([['purchase_id','=',compra.id]])
            datP.write({'location_id':8})
            datP.write({'origin':orden.name})
            datP.action_confirm()
            datP.action_assign()    
        name = 'Picking'
        res_model = 'stock.picking' 
        view_name = 'stock.view_picking_form'
        view = self.env.ref(view_name)
        return {
            'name': _('Transferencia'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.picking',
            #'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'current',
            'res_id': pick_origin.id if(pick_origin!=[]) else pick_origin1.id,
            'nodestroy': True
        }




class TransferInterMoveTemp(TransientModel):
    _name='transferencia.interna.temp'
    _description='Lineas Temporales Transferencia'
    producto=fields.Many2one('product.product')
    modelo=fields.Char(related='producto.name',string='Modelo')
    noParte=fields.Char(related='producto.default_code',string='No. Parte')
    descripcion=fields.Text(related='producto.description',string='Descripción')
    #stoc=fields.Many2one('stock.quant',string='Existencia')
    cantidad=fields.Integer('Demanda Inicial')
    almacen=fields.Many2one('stock.warehouse','Almacén Origen')
    ubicacion=fields.Many2one('stock.location','Ubicación')
    disponible=fields.Float(compute='almac',string='Disponible')
    transfer=fields.Many2one('transferencia.interna')
    unidad=fields.Many2one('uom.uom',related='producto.uom_id')
    categoria=fields.Many2one('product.category')
    serie=fields.Many2one('stock.production.lot',store=True)

    @api.depends('almacen','producto')
    def almac(self):
        res={}
        for record in self:
            if(record.almacen):
                ex=self.env['stock.quant'].search([['location_id','=',record.almacen.lot_stock_id.id],['product_id','=',record.producto.id]]).sorted(key='quantity',reverse=True)
                record.disponible=int(ex[0].quantity) if(len(ex)>0) else 0




    # @api.onchange('producto')
    # def quant(self):
    #     res={}
    #     if(self.producto):
    #         self.disponible=0
    #         h=self.env['stock.quant'].search([['product_id','=',self.producto.id],['location_id','=',self.ubicacion.id],['quantity','>',0]])
    #         if(len(h)>0 and self.producto.categ_id.id!=13):
    #             self.stoc=h.id
    #         if(len(h)==0 and self.producto.categ_id.id!=13):
    #             d=self.env['stock.location'].search([['location_id','=',self.ubicacion.id]])
    #             for di in d:
    #                 i=self.env['stock.quant'].search([['product_id','=',self.producto.id],['location_id','=',di.id],['quantity','>',0]])
    #                 if(len(i)>0):
    #                     self.stoc=i.id
    #         if(self.producto.categ_id.id==13):
    #             self.disponible=len(h)
    #             self.cantidad=1
    #             res['domain']={'serie':[('id','in',h.mapped('lot_id.id'))]}
    #             return res
                

class PickingSerie(TransientModel):
    _name='picking.serie'
    _description='Seleccion Serie'    
    pick=fields.Many2one('stock.picking')
    lines=fields.One2many('picking.serie.line','rel_picki_serie')


    def confirmar(self):
        for s in self.lines:
            d=self.env['stock.move.line'].search([['move_id','=',s.move_id.id]])
            d.write({'lot_id':s.serie.id})
        return 0

class PickingSerieLine(TransientModel):
    _name='picking.serie.line'
    _description='lines temps'
    producto=fields.Many2one('product.product')
    serie=fields.Many2one('stock.production.lot',domain="['&',('product_id.id','=',producto),('x_studio_estado','=',estado)]")
    estado=fields.Selection([["Obsoleto","Obsoleto"],["Usado","Usado"],["Hueso","Hueso"],["Para reparación","Para reparación"],["Nuevo","Nuevo"],["Buenas condiciones","Buenas condiciones"],["Excelentes condiciones","Excelentes condiciones"],["Back-up","Back-up"],["Dañado","Dañado"]])
    modelo=fields.Many2one(related='serie.product_id')
    rel_picki_serie=fields.Many2one('picking.serie')
    color=fields.Selection([('B/N','B/N'),('Color', 'Color')])
    contadorMono=fields.Integer('Contador Monocromatico')
    contadorColor=fields.Integer('Contador Color')
    move_id=fields.Many2one('stock.move')
    @api.onchange('producto')
    def color(self):
        if(self.producto):
            self.color=self.producto.x_studio_color_bn

class StockPickingMassAction(TransientModel):
    _name = 'stock.move.action'
    _description = 'Reporte de Movimientos'
    picking_ids = fields.Many2many(comodel_name="stock.move")
    almacen=fields.Many2one('stock.warehouse')
    categoria=fields.Many2one('product.category')
    tipo=fields.Selection([["Entrada","Entrada"],["Salida","Salida"],["Todos","Todos"]],default="Todos")
    fechaInicial=fields.Datetime()
    fechaFinal=fields.Datetime()

    def report(self):
        move=None
        mov=self.env['stock.move.line'].search(['&','&',['state','=','done'],['date','>=',self.fechaInicial],['date','<=',self.fechaFinal]])
        move=mov
        origenes=[]
        destinos=[]
        if(self.almacen.id==False):
            almacenes=self.env['stock.warehouse'].search([['x_studio_cliente','=',False]])
            for alm in almacenes:
                b=alm.lot_stock_id.id
                c=alm.lot_stock_id.id
                if(self.tipo=="Todos"):
                    origenes.append(b)
                    destinos.append(c)
                if(self.tipo=="Entrada"):
                    destinos.append(c)
                if(self.tipo=="Salida"):
                    origenes.append(b)
        if(self.almacen.id):
            b=self.almacen.lot_stock_id.id
            c=self.almacen.lot_stock_id.id
            if(self.tipo=="Todos"):
                origenes.append(b)
                destinos.append(c)
            if(self.tipo=="Entrada"):
                destinos.append(c)
            if(self.tipo=="Salida"):
                origenes.append(b)
        if(self.categoria):
            mov=mov.filtered(lambda x: x.x_studio_field_aVMhn.id==self.categoria.id)
        if(self.categoria==False):
            categorias=self.env['product.category'].search([['id','!=',13]]).mapped('id')
            mov=mov.filtered(lambda x: x.x_studio_field_aVMhn.id in categorias)
        mov=mov.filtered(lambda x: x.location_id.id in origenes or x.location_dest_id.id in destinos)
        if(len(mov)>1):
            mov[0].write({'x_studio_arreglo':mov.mapped('id')})
            return self.env.ref('stock_picking_mass_action.partner_xlsx').report_action(mov[0])
        if(len(mov)==0):
            raise UserError(_("No hay registros para la selecion actual"))

class StockQuantMassAction(TransientModel):
    _name = 'stock.quant.action'
    _description = 'Reporte de Existencias'
    quant_ids = fields.Many2many(comodel_name="stock.quant")
    almacen=fields.Many2many('stock.warehouse')
    categoria=fields.Many2one('product.category')
    tipo=fields.Many2one('product.product',string='Modelo')
    equipo =fields.Boolean('Equipos')
    estado=fields.Selection([["Obsoleto","Obsoleto"],["Usado","Usado"],["Hueso","Hueso"],["Para reparación","Para reparación"],["Nuevo","Nuevo"],["Buenas condiciones","Buenas condiciones"],["Excelentes condiciones","Excelentes condiciones"],["Back-up","Back-up"],["Dañado","Dañado"]])
    anterior=fields.Boolean()
    fecha=fields.Date()
    regi=fields.Integer()
    archivo=fields.Binary()




    def report(self):
        if(self.anterior):
            if(self.fecha):
                registro=self.env['quant.history'].search([['fecha','=',self.fecha]])
                if(registro.id):
                    self['regi']=registro.id
                    self['archivo']=registro.reporte
                else:
                    raise UserError(_("No hay registros para la selecion actual"))
            else:
                raise UserError(_("Debe ingresar la fecha deseada"))

        if(self.anterior==False):    
            d=[]
            if(len(self.almacen)>0):
                d.append(['location_id','in',self.almacen.mapped('lot_stock_id.id')])
            if(self.categoria):
                d.append(['x_studio_categoria','=',self.categoria.id])
                if(self.categoria.id==13):
                    d.append(['x_studio_almacn.x_studio_cliente','=',False])
                    if(self.almacen):
                        d.append(['location_id','in',self.almacen.mapped('lot_stock_id.id')])
                    if(len(self.almacen)==0):
                        d.append(['x_studio_almacn','!=',False])
            if(self.tipo):
                d.append(['product_id','=',self.tipo.id])
            if(self.estado):
                d.append(['lot_id.x_studio_estado','=',self.estado])
            data=self.env['stock.quant'].search(d,order="x_studio_almacn")
            if(len(data)>0):
                data[0].write({'x_studio_arreglo':str(data.mapped('id'))})
                return self.env.ref('stock_picking_mass_action.quant_xlsx').report_action(data[0])        
            if(len(data)==0):
                raise UserError(_("No hay registros para la selecion actual"))

class SaleOrderMassAction(TransientModel):
    _name = 'sale.order.action'
    _description = 'Reporte de Solicitudes'
    fechaInicial=fields.Datetime()
    fechaFinal=fields.Datetime()
    tipo=fields.Selection([["Cambio","Cambio"],["Arrendamiento","Arrendamiento"],["Venta","Venta"],["Backup","Backup"],["Demostración","Demostración"],["Retiro","Retiro"],["Préstamo","Préstamo"]])
    def report(self):
        i=[]
        d=[]
        if(self.fechaInicial):
            m=['confirmation_date','>=',self.fechaInicial]
            i.append(m)
        if(self.fechaFinal):
            m=['confirmation_date','<=',self.fechaFinal]
            i.append(m)
        if(self.tipo):
            m=['x_studio_tipo_de_solicitud','=',self.tipo]
            i.append(m)
        i.append(['x_studio_field_bxHgp','=',False])
        d=self.env['sale.order'].search(i,order='confirmation_date asc').filtered(lambda x:x.origin==False and x.x_studio_factura==False)
        if(len(d)>0):
            d[0].write({'x_studio_arreglo':str(d.mapped('id'))})
            return self.env.ref('stock_picking_mass_action.sale_xlsx').report_action(d[0])
        if(len(d)==0):
            raise UserError(_("No hay registros para la selecion actual"))

class HelpdeskTicketMassAction(TransientModel):
    _name = 'helpdesk.ticket.action'
    _description = 'Reporte de Tickets'
    fechaInicial=fields.Datetime()
    fechaFinal=fields.Datetime()
    estado=fields.Many2one('helpdesk.state')
    tipo=fields.Selection([["Falla","Falla"],["Toner","Toner"]])
    area=fields.Many2one('helpdesk.team')
    fechaauto=fields.Boolean('Fecha Automatica',default=True)

    @api.onchange('fechaauto')
    def automatica(self):
        if(self.fechaauto==True):
            fecha=datetime.datetime.now()
            fecha2=fecha-datetime.timedelta(days=90)
            self.fechaInicial=fecha2
            self.fechaFinal=fecha



    def report(self):
        i=[]
        d=[]
        j=[]
        if(self.fechaInicial):
            m=['create_date','>=',self.fechaInicial]
            i.append(m)
        if(self.fechaFinal):
            m=['create_date','<=',self.fechaFinal]
            i.append(m)
        j.append('|')
        if(self.tipo):
            if(self.tipo=="Toner"):
                m=['team_id.id','=',8]
                i.append(m)
            else:
                m=['team_id.id','!=',8]
                i.append(m)
        i.append(['x_studio_field_nO7Xg','!=',False])
        d=self.env['helpdesk.ticket'].search(i,order='create_date asc').filtered(lambda x:len(x.x_studio_equipo_por_nmero_de_serie_1)>0 or len(x.x_studio_equipo_por_nmero_de_serie)>0)
        if(len(d)>0):
            d[0].write({'x_studio_arreglo':str(d.mapped('id'))})
            return self.env.ref('stock_picking_mass_action.ticket_xlsx').report_action(d[0])
        if(len(d)==0):
            raise UserError(_("No hay registros para la selecion actual"))


class SolicitudestockInventoryMassAction(TransientModel):
    _name = 'stock.inventory.action'
    _description = 'Importacion Inventario'
    almacen=fields.Many2one('stock.warehouse',domain="[('x_studio_cliente','=',False)]")
    archivo=fields.Binary()
    comentario=fields.Char()


    def importacion(self):
        if(self.archivo):
            f2=base64.b64decode(self.archivo)
            H=StringIO(f2)
            mimetype = guess_mimetype(f2 or b'')
            if(mimetype=='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or mimetype=='application/vnd.ms-excel'):
                book = xlrd.open_workbook(file_contents=f2 or b'')
                sheet = book.sheet_by_index(0)
                header=[]
                arr=[]
                i=0
                id3=self.env['stock.inventory'].create({'name':str(self.comentario)+' '+str(self.almacen.name), 'location_id':self.almacen.lot_stock_id.id,'x_studio_field_8gltH':self.almacen.id,'state':'done'})
                for row_num, row in enumerate(sheet.get_rows()):
                    if(i>0):
                        print(row[1].value)
                        ubicacion=None
                        template=self.env['product.template'].search([('default_code','=',str(row[1].value).replace('.0',''))]).sorted(key='id',reverse=True)
                        productid=self.env['product.product'].search([('product_tmpl_id','=',template[0].id if(len(template)>1) else template.id)])
                        if(productid.id==False):
                            productid=self.env['product.product'].create({'name':row[0].value,'default_code':row[1].value,'description':row[4].value})
                        quant={'product_id':productid.id,'reserved_quantity':'0','quantity':row[2].value, 'location_id':self.almacen.lot_stock_id.id}
                        inventoty={'inventory_id':id3.id, 'partner_id':'1','product_id':productid.id,'product_uom_id':'1','product_qty':row[2].value, 'location_id':self.almacen.lot_stock_id.id}
                        if(row[3].ctype!=0 and row[3].value!=''):
                            ubicacion=self.env['x_ubicacion_inventario'].search([('x_name','=',str(row[3].value).replace('.0',''))])
                            if(len(ubicacion)==0):
                                ubicacion=self.env['x_ubicacion_inventario'].create({'x_name':str(row[3].value).replace('.0','')})
                        if(row[4].ctype!=0 and row[4].value!=''):
                            serie=self.env['stock.production.lot'].search([('name','=',str(row[3].value).replace('.0',''))])
                            inventoty['prod_lot_id']=serie.id
                            quant['lot_id']=serie.id
                        if(ubicacion!=None):
                            inventoty['x_studio_field_yVDjd']=ubicacion.id
                        self.env['stock.inventory.line'].create(inventoty)
                        busqueda=self.env['stock.quant'].search([['product_id','=',productid.id],['location_id','=',self.almacen.lot_stock_id.id]])
                        if(len(busqueda)>0):
                            jj=0
                            if(len(busqueda)>1):
                                for b in busqueda:
                                    if(jj>0):
                                        b.unlink()
                                    jj=jj+1
                            if(ubicacion!=None):
                                busqueda[0].sudo().write({'quantity':row[2].value,'x_studio_field_kUc4x':ubicacion.id})                            
                            else:
                                busqueda[0].sudo().write({'quantity':row[2].value})
                        if(len(busqueda)==0):
                            if(ubicacion!=None):
                                quant['x_studio_field_kUc4x']=ubicacion.id
                            else:
                                self.env['stock.quant'].sudo().create(quant)
                    i=i+1
            else:
                raise UserError(_("Archivo invalido"))

class PickingsAComprasMassAction(TransientModel):
    _name = 'stock.pickings.compras'
    _description = 'Picking a compras'
    
    def _default_picking_ids(self):
        return self.env['stock.picking'].browse(
            self.env.context.get('active_ids'))

    picking_ids = fields.Many2many(
        string='Pickings',
        comodel_name="stock.picking",
        default=lambda self: self._default_picking_ids(),
        help="",
    )

    def confirmar(self):
        requLin=[]
        pi=[]
        requisiociones=self.env['requisicion.requisicion'].search([])
        test=requisiociones.mapped('picking_ids.id')
        for pick in self.picking_ids:
            e=[]
            if(pick.id not in test):
                for move in pick.move_ids_without_package:
                    d=self.env['stock.quant'].search([['location_id','=',move.location_id.id],['product_id','=',move.product_id.id]]).sorted(key='quantity',reverse=True)
                    if(d.quantity==0):
                        requisicionline={'cliente':move.picking_id.partner_id.id,'ticket':move.picking_id.x_studio_ticket_relacionado.id,'product':move.product_id.id,'cantidad':move.product_uom_qty,'costo':0}
                        requLin.append(requisicionline)
                        e.append(move.picking_id.id)
                if(e!=[]):
                    pi.append(e[0])
        if(len(requLin)>0):
            requisicion=self.env['requisicion.requisicion'].create({'area':'Almacen','fecha_prevista':datetime.datetime.now(),'justificacion':'Falta de stock','state':'open','picking_ids':[(6,0,pi)]})
            for r in requLin:
                r['req_rel']=requisicion.id
                self.env['product.rel.requisicion'].create(r)
            for pp in self.picking_ids:
                pp.x_studio_ticket_relacionado.write({'stage_id':113})
                self.env['helpdesk.diagnostico'].sudo().create({ 'write_uid': self.env.user.name,'ticketRelacion' : pp.x_studio_ticket_relacionado.id, 'estadoTicket' : "Pendiente de compra", 'comentario':"Pendiente de compra Requisicion:("+requisicion.name+")"}) 
            view = self.env.ref('studio_customization.default_form_view_fo_24cee64e-ad11-4f19-a7f6-fceca5375726')
            return {
                    'name': _('Transferencia'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'requisicion.requisicion',
                    #'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target': 'current',
                    'res_id': requisicion.id,
                    'nodestroy': True
                    }
        else:
            return {'warning': {
            'title': _('Alerta'),
            'message': ('Las ordenes selcciondas tiene existencias o ya se encuntran con una requisicion.')
                    }}
class ProductAltaAction(TransientModel):
    _name = 'product.product.action'
    _description='Alta de referencias en masa'
    archivo=fields.Binary()
    almacen=fields.Many2one('stock.warehouse')

    def crear(self):
        if(self.archivo):
            f2=base64.b64decode(self.archivo)
            H=StringIO(f2)
            mimetype = guess_mimetype(f2 or b'')
            if(mimetype=='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or mimetype=='application/vnd.ms-excel'):
                book = xlrd.open_workbook(file_contents=f2 or b'')
                sheet = book.sheet_by_index(0)
                header=[]
                arr=[]
                i=0
                j=0
                check=False
                for row_num, row in enumerate(sheet.get_rows()):
                    if(j>0):
                        if(row[2].ctype!=0):
                            if(row[2].value!=''):
                                if(int(row[2].value)>0):
                                    check=True
                    j=j+1
                id3=None
                if(check and self.almacen.id==False):
                    raise UserError(_("Se requiere almacen para cargar las existencias"))
                if(check and self.almacen.id!=False):
                    id3=self.env['stock.inventory'].create({'name':'Carga de creacion'+str(self.almacen.name), 'location_id':self.almacen.lot_stock_id.id,'x_studio_field_8gltH':self.almacen.id,'state':'done'})
                for row_num, row in enumerate(sheet.get_rows()):
                    if(i>0):
                        template=self.env['product.template'].search([('name','=',str(row[0].value).replace('.0','')),('categ_id', '=',13)])
                        productid=self.env['product.product'].search([('product_tmpl_id','=',template.id)])
                        unidad=self.env['uom.uom'].search([('name','=','Unidad(es)' if(row[3].value.lower()=='pieza') else row[3].value)])
                        producto=self.env['product.product'].search([['default_code','=',str(row[1].value).replace('.0','')]])
                        inventario=self.env['stock.quant'].search([['product_id','=',producto.id],['location_id','=',self.almacen.lot_stock_id.id]])
                        categoria=self.env['product.category'].search([['name','=',row[5].value]])
                        if(producto.id==False):
                            producto=self.env['product.product'].create({'default_code':str(row[1].value).replace('.0',''),'categ_id':categoria.id,'x_studio_field_ry7nQ':productid.id,'description':row[4].value,'name':row[0].value,'uom_id':unidad.id if(unidad.id) else False})
                        if(check):
                            if(self.almacen):
                                quant={'product_id':producto.id,'reserved_quantity':'0','quantity':row[2].value, 'location_id':self.almacen.lot_stock_id.id}
                                inventoty={'inventory_id':id3.id, 'partner_id':'1','product_id':productid.id,'product_uom_id':'1','product_qty':row[2].value, 'location_id':self.almacen.lot_stock_id.id}
                                if(inventario.id):
                                    inventario.write({'quantity':row[2].value})
                                if(inventario.id==False):
                                    self.env['stock.quant'].sudo().create(quant)
                                self.env['stock.inventory.line'].create(inventoty)
                            else:
                                raise UserError(_("Se requiere almacen para cargar las existencias"))
                    i=i+1
            else:
                raise UserError(_("Archivo invalido"))
class  DevolverPick(TransientModel):
    _name='devolver.action'
    _description='devolucion a almacen'
    fecha=fields.Datetime()
    comentario=fields.Char()
    picking=fields.Many2one('stock.picking')
    tipo=fields.Selection([["Total","Total"],["Parcial","Parcial"]])

    def confirmar(self):
        pic=self.env['stock.picking'].search([['id','=',self.picking.id]])
        destino=None
        sale=self.env['sale.order'].search([['id','=',self.picking.sale_id.id]])
        ticket_id=sale.x_studio_field_bxHgp.id
        if(self.picking.picking_type_id.warehouse_id.id==1):
            destino=self.env['stock.picking.type'].search([['name','=','Recepciones'],['warehouse_id','=',self.picking.picking_type_id.warehouse_id.id]])
        if(self.picking.picking_type_id.warehouse_id.id!=1):
            destino=self.env['stock.picking.type'].search([['name','=','Receipts'],['warehouse_id','=',self.picking.picking_type_id.warehouse_id.id]])
        pick_origin1= self.env['stock.picking'].create({'picking_type_id' : destino.id,'almacenOrigen':self.picking.picking_type_id.warehouse_id.id,'almacenDestino':self.picking.picking_type_id.warehouse_id.id,'location_id':self.picking.location_id.id,'location_dest_id':self.picking.picking_type_id.warehouse_id.lot_stock_id.id})
        for l in self.picking.move_ids_without_package:
            datos1={'picking_id':pick_origin1.id,'product_id' : l.product_id.id, 'product_uom_qty' : l.product_uom_qty,'name':l.name if(l.product_id.description) else '/','product_uom':l.product_uom.id,'location_id':self.picking.location_id.id,'location_dest_id':self.picking.picking_type_id.warehouse_id.lot_stock_id.id}
            self.env['stock.move'].create(datos1)
        self.picking.action_cancel()
        pick_origin1.write({'x_studio_ticket':sale.origin})
        pick_origin1.write({'partner_id':self.picking.partner_id.id})
        pick_origin1.write({'distribucion':True})
        pick_origin1.action_assign()
        pick_origin1.action_confirm()
        if(self.tipo=="Parcial"):
            sale.write({'x_studio_field_bxHgp':False})
            s=sale.copy()
            s.write({'x_studio_field_bxHgp':ticket_id})
            sale.write({'x_studio_field_bxHgp':ticket_id})
            s.write({'x_studio_fecha_de_entrega':self.fecha,'commitment_date':self.fecha})
            s.action_confirm()
            self.picking.x_studio_ticket_relacionado.write({'x_studio_field_0OAPP':[(4,s.id)]})
        self.env['helpdesk.diagnostico'].sudo().create({ 'write_uid': self.env.user.name,'ticketRelacion' : self.picking.sale_id.x_studio_field_bxHgp.id, 'create_uid' : self.env.user.id, 'estadoTicket' : "Devuelto a Almacen", 'comentario':self.comentario}) 
        
class StockQua(TransientModel):
    _name='quant.action'
    _description='Ajuste en quant'
    quant=fields.Many2one('stock.quant')
    producto=fields.Many2one('product.product')
    cantidad=fields.Float()
    ubicacion=fields.Many2one('x_ubicacion_inventario')
    comentario=fields.Char()
    usuario=fields.Many2one('res.users')

    def confirmar(self):
        self.env['stock.quant.line'].sudo().create({'quant_id':self.quant.id,'descripcion':self.comentario,'cantidadAnterior':self.quant.quantity,'cantidadReal':self.cantidad,'usuario':self.usuario.id})
        self.quant.sudo().write({'quantity':self.cantidad,'x_studio_field_kUc4x':self.ubicacion.id})

class SerieIngreso(TransientModel):
    _name='serie.ingreso'
    _description='Ingreso desde proveedor'
    picking=fields.Many2one('stock.picking')
    lineas=fields.One2many('serie.ingreso.line','serie_rel')
    almacen=fields.Many2one('stock.warehouse','Almacen')
    archivo=fields.Binary('Archivo')

    def confirmar(self):
        for mv in self.lineas:
            mv.write({'location_dest_id':self.almacen.lot_stock_id.id})
            if(mv.producto.categ_id.id!=13):
                mv.move_line.write({'location_dest_id':self.almacen.lot_stock_id.id,'qty_done':mv.cantidad})
            if(mv.producto.categ_id.id==13 and mv.serie_name!=False):
                mv.move_line.write({'location_dest_id':self.almacen.lot_stock_id.id,'lot_name':mv.serie_name,'qty_done':mv.cantidad})
        #if(len(self.lineas.mapped('serie_name'))!=[]):
        self.picking.action_done()
        self.picking.purchase_id.write({'recibido':'recibido'})
        self.env['stock.picking'].search([['state','=','assigned']]).action_assign()
        return self.env.ref('stock.action_report_picking').report_action(self.picking)



class SerieIngresoLine(TransientModel):
    _name='serie.ingreso.line'
    _description='Lineas de ingreso equipos'
    producto=fields.Many2one('product.product','Modelo')
    cantidad=fields.Float('Cantidad')
    serie=fields.Many2one('stock.production.lot')
    serie_name=fields.Char()
    serie_rel=fields.Many2one('serie.ingreso')
    move_line=fields.Many2one('stock.move.line')
    categoria=fields.Integer()

class AddCompatibles(TransientModel):
    _name='add.compatible'
    _description='Agregar Compatibles'
    productoInicial=fields.Many2one('product.product')
    productoCompatible=fields.Many2one('product.product')

    def confirmar(self):
        self.productoInicial.write({'x_studio_toner_compatible':[(4,self.productoCompatible.id)]})

class ReporteCompras(TransientModel):
    _name='purchase.order.action'
    _description='Reporte de compras'
    fechaInicial=fields.Datetime()
    fechaFinal=fields.Datetime()
    tipo=fields.Selection([["Pagos","Pagos"],["Compras","Compras"]])
    usuario=fields.Selection([["Claudia Moreno","Claudia Moreno"],["Veronica Aparicio","Veronica Aparicio"]])

    def report(self):
        i=[]
        d=[]
        j=[]
        if(self.fechaInicial):
            m=['date_planned','>=',self.fechaInicial]
            i.append(m)
        if(self.fechaFinal):
            m=['date_planned','<=',self.fechaFinal]
            i.append(m)
        if(self.usuario=="Claudia Moreno"):
            m=['x_studio_claudia','=',True]
            i.append(m)
        if(self.usuario=="Veronica Aparicio"):
            m=['x_studio_vernica','=',True]
            i.append(m)
        if(self.tipo=="Pagos"):
            m=['x_studio_impuesto','!=',0]
            i.append(m)
        if(self.tipo=="Compras"):
            i.append(['state','=','purchase'])    
        d=self.env['purchase.order'].search(i,order='date_planned asc')
        d[0].write({'x_studio_arreglo':str(d.mapped('id'))})
        return self.env.ref('stock_picking_mass_action.compras_xlsx').report_action(d[0])

class AltaProductoOne(TransientModel):
    _name='product.product.one'
    _description='Alta de referencia'
    modelo=fields.Char()
    noParte=fields.Char()
    descripcion=fields.Char()
    almacen=fields.Many2one('stock.warehouse',domain=[['x_studio_cliente','=',False]])
    tipo=fields.Many2one('product.category')
    existencia=fields.Float()

    def crear(self):
        find=self.env['product.product'].search([['default_code','ilike',self.noParte.replace(' ','').replace('-','')],['categ_id','=',self.tipo.id]])
        if(find.id):
            if(self.almacen.id):
                quant=self.env['stock.quant'].search([['product_id','=',find.id],['location_id','=',self.almacen.lot_stock_id.id]])
                if(quant.id):
                    if(self.existencia!=0):
                        quant.write({'quantity':self.existencia})
                else:
                    self.env['stock.quant'].sudo().create({'product_id':find.id,'location_id':self.almacen.lot_stock_id.id,'quantity':self.existencia})
        else:
            p=self.env['product.product'].create({'name':self.modelo,'default_code':self.noParte,'description':self.descripcion,'categ_id':self.tipo.id})
            if(self.almacen.id):
                self.env['stock.quant'].sudo().create({'product_id':p.id,'location_id':self.almacen.lot_stock_id.id,'quantity':self.existencia})


class AltaProductoOne(TransientModel):
    _name='stock.warehouse.orderpoint.import'
    _description='Importacion de reglas o actulización'
    archivo=fields.Binary()



    def importar(self):
        if(self.archivo):
            f2=base64.b64decode(self.archivo)
            H=StringIO(f2)
            mimetype = guess_mimetype(f2 or b'')
            if(mimetype=='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or mimetype=='application/vnd.ms-excel'):
                book = xlrd.open_workbook(file_contents=f2 or b'')
                sheet = book.sheet_by_index(0)
                header=[]
                arr=[]
                i=0
                j=0
                check=False
                for row_num, row in enumerate(sheet.get_rows()):
                    if(i!=0):
                        almacen=self.env['stock.warehouse'].search([['name','ilike',str(row[0].value).lower()],['x_studio_cliente','=',False]])
                        producto=self.env['product.product'].search([['default_code','=',str(row[2].value).replace(' ','')]])
                        regla=self.env['stock.warehouse.orderpoint'].search([['location_id','=',almacen.lot_stock_id.id],['product_id','=',producto.id]])
                        if(regla.id):
                            regla.write({'product_min_qty':row[3].value,'product_max_qty':row[4].value})
                        else:
                            self.env['stock.warehouse.orderpoint'].create({'location_id':almacen.lot_stock_id.id,'product_id':producto.id,'product_min_qty':row[3].value,'product_max_qty':row[4].value})
                    i=i+1
            else:
                raise UserError(_("Error en el formato del archivo"))


class detalleTicket(TransientModel):
    _name='helpdesk.detalle.ticket'
    _description='detalle del ticket'
    ticket=fields.Many2one('helpdesk.ticket')
    series=fields.Many2many('stock.production.lot')
    historico=fields.One2many(related='ticket.diagnosticos')
    cliente=fields.Many2one(related='ticket.partner_id')
    localidad=fields.Many2one(related='ticket.x_studio_empresas_relacionadas')
    solicitud=fields.Many2one(related='ticket.x_studio_field_nO7Xg')
    pedido=fields.One2many(related='solicitud.order_line')
    backorders=fields.One2many(related='ticket.x_studio_backorder')
    estado=fields.Many2one(related='ticket.stage_id')
    area=fields.Many2one(related='ticket.team_id')
    ejecutivo=fields.Many2one(related='ticket.user_id')
    tecnico=fields.Many2one(related='ticket.x_studio_tcnico')
    zona=fields.Selection(related='ticket.x_studio_zona')
    dias=fields.Integer(related='ticket.days_difference')
    idTicket=fields.Integer()    

    @api.onchange('idTicket')
    def searchTicket(self):
        if(self.idTicket):
            self.ticket=self.env['helpdesk.ticket'].search([['id','=',self.idTicket]]).id

    @api.onchange('ticket')
    def seriesAsignadas(self):
        if(self.ticket):
            uno=self.ticket.mapped('x_studio_equipo_por_nmero_de_serie.id')
            dos=self.ticket.mapped('x_studio_equipo_por_nmero_de_serie_1.serie.id')
            self.series=[(5,0,0)]
            self.series=uno if(uno!=[]) else dos


class reporteCreacionRuta(TransientModel):
    _name='reporte.creacion.ruta'
    _description='Reporte de creacion de ruta'
    name=fields.Char()

    def reporte(self):
        d=self.env['creacion.ruta'].search([['ordenes','!=',False]],order='create_date desc')
        d[0].write({'arreglo':d.mapped('id')})
        return self.env.ref('stock_picking_mass_action.ruta_xlsx').report_action(d[0])

class agregarConcentrado(TransientModel):
    _name='stock.picking.mass.concentrado'
    _description='Agregar concentrado'
    def _default_picking_ids(self):
        return self.env['stock.picking'].browse(
            self.env.context.get('active_ids'))
    picking_ids = fields.Many2many(
        string='Pickings',
        comodel_name="stock.picking",
        default=lambda self: self._default_picking_ids(),
        help="",
    )

    def concentrar(self):
        CON=str(self.env['ir.sequence'].next_by_code('concentrado'))
        for pic in self.picking_ids:
            self.env['stock.picking'].search([['sale_id','=',pic.sale_id.id]]).write({'concentrado':CON})
        return self.env.ref('stock_picking_mass_action.report_custom').report_action(self.picking_ids)

class cargadeGuias(TransientModel):
    _name='ticket.guia.carga'
    _description='Carga de Guias a Ticket'
    archivo=fields.Binary()


    def carga(self):
        if(self.archivo):
            f2=base64.b64decode(self.archivo)
            H=StringIO(f2)
            mimetype = guess_mimetype(f2 or b'')
            if(mimetype=='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or mimetype=='application/vnd.ms-excel'):
                book = xlrd.open_workbook(file_contents=f2 or b'')
                sheet = book.sheet_by_index(0)
                header=[]
                arr=[]
                i=0
                j=0
                check=False
                for row_num, row in enumerate(sheet.get_rows()):
                    if(i>3):
                        if("EQUIPO" not in str(row[3].value)):
                            Tickets=str(row[3].value).replace('REF','').replace(' ','').replace('.0','').split('-')
                            for t in Tickets:
                                tt=int(t)
                                self.env.cr.execute("update helpdesk_ticket set x_studio_nmero_de_guia_1="+str(int(row[2].value))+" where id="+str(tt)+";")            
                    i=i+1
            else:
                raise UserError(_("Error en el formato del archivo"))

class reporteBaseInslada(TransientModel):
    _name='lot.serial.reporte'
    _description='reporte de base instala wizard'

    def reporte(self):
        s=self.env['stock.production.lot'].search([['servicio','!=',False]])
        s[0].write({'x_studio_arreglo':str(s.mapped('id'))})
        return self.env.ref('stock_picking_mass_action.serie_xlsx').report_action(s[0])


class assignacionAccesorios(TransientModel):
    _name='lot.assign.accesorios'
    _description='Asignacion de accesorios'
    lineas=fields.One2many('lot.assign.accesorios.lines','rel_id')
    pick=fields.Many2one('stock.picking')
    domain=fields.Char()

    @api.onchange('domain')
    def limitacion(self):
        res={}
        res['domain']={'lineas':[['id','in',eval(self.domain)]]}
        return res

    def confirmar(self):
        for line in  self.lineas:
            if(len(line.accesorios)!=0):
                line.lot_id.write({'x_studio_field_SOEw0':[(6, 0, line.mapped('accesorios.id'))]})
        wiz=self.env['stock.picking.mass.action'].create({'picking_ids':[(4,self.pick.id)],'confirm':True,'check_availability':True,'transfer':True})
        view = self.env.ref('stock_picking_mass_action.view_stock_picking_mass_action_form')
        return {
            'name': _('Transferencia'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.picking.mass.action',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
            }


class assignacionAccesoriosLines(TransientModel):
    _name='lot.assign.accesorios.lines'
    _description='Asignacion de accesorios lines'
    rel_id=fields.Many2one('lot.assign.accesorios')
    lot_id=fields.Many2one('stock.production.lot')
    accesorios=fields.Many2many('product.product')


class entregaRefacciones(TransientModel):
    _name='entrega.action'
    _description='Entrega Refacciones'
    pick=fields.Many2one('stock.picking')
    lines=fields.One2many('entrega.refacciones.lines','rel_id')
    tecnico=fields.Many2one('hr.employee')
    
    def confirmar(self):
        self.pick.action_assign()
        self.env['helpdesk.diagnostico'].create({ 'write_uid': self.env.user.name,'ticketRelacion' : self.pick.sale_id.x_studio_field_bxHgp.id, 'create_uid' : self.env.user.id,'write_uid':self.env.user.id, 'estadoTicket' : "Entregado", 'comentario':' Entregado a '+self.tecnico.name+' Hecho por'+self.env.user.name})
        for l in self.lines:
            m=self.env['stock.move.line'].search([['move_id','=',l.move_id.id]])
            m.write({'quantity_done':l.cantidadE})
        wiz=self.env['stock.picking.mass.action'].create({'picking_ids':[(4,self.pick.id)],'confirm':True,'check_availability':True,'transfer':True})
        wiz.mass_action()

    
    
    
class entregaRefaccionesLines(TransientModel):
    _name='entrega.refacciones.lines'
    _description='Entrega Refacciones Lines'
    rel_id=fields.Many2one('entrega.action')
    move_id=fields.Many2one('stock.move')
    product_id=fields.Many2one('product.product')
    cantidadS=fields.Float()
    cantidadE=fields.Float()



class assignacionAccesorios(TransientModel):
    _name='lot.retiro'
    _description='Retiro de series'
    lineas=fields.One2many('lot.retiro.lines','rel_id')
    pick=fields.Many2one('stock.picking')

    def confirmar(self):
        for line in  self.lineas:
            line.move_id.write({'location_dest_id':line.almacen.lot_stock_id.id})
            line.move_line.write({'location_dest_id':line.almacen.lot_stock_id.id})
            line.serie.write({'x_studio_estado':line.estado})
            da={'porcentajeNegro':line.nivelNegro,'porcentajeAmarillo':line.nivelAmarillo,'porcentajeCian':line.nivelCian,'porcentajeMagenta':line.nivelMagenta,'contadorColor':line.contadorColor,'x_studio_toner_negro':1,'x_studio_toner_amarillo':1,'x_studio_toner_cian':1,'x_studio_toner_magenta':1,'contadorMono':line.contadorMono,'serie':line.serie.id,'fuente':'stock.production.lot'}
            c=self.env['dcas.dcas'].create(da)
            a=c.copy()
            b=c.copy()
            d=c.copy()
            a.write({'fuente':'dcas.dcas'})
            b.write({'fuente':'helpdesk.ticket'})
            d.write({'fuente':'tfs.tfs'})
        wiz=self.env['stock.picking.mass.action'].create({'picking_ids':[(4,self.pick.id)],'confirm':True,'check_availability':True,'transfer':True})
        wiz.mass_action()

class assignacionAccesoriosLines(TransientModel):
    _name='lot.retiro.lines'
    _description='Lineas de retiro serie'
    rel_id=fields.Many2one('lot.retiro')
    serie=fields.Many2one('stock.production.lot')
    estado=fields.Selection([["Obsoleto","Obsoleto"],["Usado","Usado"],["Hueso","Hueso"],["Para reparación","Para reparación"],["Nuevo","Nuevo"],["Buenas condiciones","Buenas condiciones"],["Excelentes condiciones","Excelentes condiciones"],["Back-up","Back-up"],["Dañado","Dañado"]])
    nota=fields.Char()
    contadorMono=fields.Integer()
    contadorColor=fields.Integer()
    nivelNegro=fields.Integer()
    nivelAmarillo=fields.Integer()
    nivelMagenta=fields.Integer()
    nivelCian=fields.Integer()
    almacen=fields.Many2one('stock.warehouse')
    move_id=fields.Many2one('stock.move')
    move_line=fields.Many2one('stock.move.line')

class reporteClientes(TransientModel):
    _name='clientes.reporte'
    _description='Reporte clientes wizard'
    clientes=fields.Many2many('res.partner')

    def reporte(self):
        if(len(self.clientes)!=0):
            c=self.env['res.partner'].search([['id','in',self.clientes.mapped('id')]])
        else:
            c=self.env['res.partner'].search([['x_studio_activo_1','=',True],['type','!=','delivery']])
        c[0].write({'arreglo':str(c.mapped('id'))})
        return self.env.ref('stock_picking_mass_action.contacto_xlsx').report_action(c[0])

class pickingDesasignar(TransientModel):
    _name='picking.desasignar'
    _description='desasignar series'
    solicitud=fields.Many2one('sale.order')

    def confirm(self):
        p=self.solicitud.picking_ids.mapped('state')
        if('done' in p):
            self.ensure_one()
            action_id = self.env.ref('stock.act_stock_return_picking')
            if(self.solicitud.id):
                pi=self.solicitud.picking_ids.filtered(lambda x:x.date_done!=False and x.state=='done').sorted(key='date_done', reverse=True)
                if(pi!=[]):
                    w=self.env['stock.return.picking'].create({'picking_id':pi[0].id,'location_id':12})
                    view=self.env.ref('stock.view_stock_return_picking_form')
                    for m in pi[0].move_ids_without_package:
                        self.env['stock.return.picking.line'].create({'wizard_id':w.id,'product_id':m.product_id.id,'move_id':m.id,'quantity':m.product_uom_qty})
                self.solicitud.write({'state':'sale','x_studio_series_retiro':False})
                self.env.cr.execute("delete stock_picking where origin='"+str(self.solicitud.name)+"';")
            return {
                    'name': _('Ingreso Series Almacen'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'stock.return.picking',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_id':w.id,
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target':'new'
                }

    @api.onchange('solicitud')
    def validacion(self):
        if(self.solicitud.id):
            p=self.solicitud.picking_ids.mapped('state')
            if('done' in p):
                mensajeCuerpo='Solicitud con Movimientos de almacen al confirmar se generara una devolucion al almacen'
                mensajeTitulo = "Alerta!!!"
                warning = {'title': _(mensajeTitulo)
                        , 'message': _(mensajeCuerpo),
                }
                return {'warning': warning}
            else:
                raise UserError(_("Solicitud sin Movimientos de almacen"))


