from odoo import _, fields, api
from odoo.models import Model
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
import logging, ast
_logger = logging.getLogger(__name__)
#puro aaa
class StockPicking(Model):
    _inherit = 'stock.picking'
    active = fields.Boolean('Active', default=True, track_visibility=True)
    almacenOrigen=fields.Many2one('stock.warehouse','Almacen Origen')
    almacenDestino=fields.Many2one('stock.warehouse','Almacen Destino')
    hiden=fields.Integer(compute='hide')
    ajusta=fields.Boolean('Ajusta',store=True)
    ajusta2=fields.Boolean(store=True)
    est = fields.Text(compute = 'x_historial_ticket_actualiza')
    backorder=fields.Char('Backorder',store=True)
    lineTemp=fields.One2many('stock.pick.temp','picking')
    estado = fields.Selection([('recepcion','Recepción'),('draft', 'Draft'),('almacen', 'Almacen'),('compras', 'Solicitud de Compra'),('waiting', 'Esperando otra operación'),('confirmed', 'Sin Stock'),('assigned', 'Por Validar'),('done', 'Validado'),('distribucion', 'Distribución'),('cancel', 'Cancelled'),('aDistribucion', 'A Distribución'),('Xenrutar', 'Por en Rutar'),('ruta', 'En Ruta'),('entregado', 'Entregado')],store=True)
    value2 = fields.Integer(store=True)
    lineasBack = fields.One2many(related='backorder_ids.move_ids_without_package')
    ruta_id=fields.Many2one('creacion.ruta')
    concentrado=fields.Char()
    mensaje=fields.Char(compute='back')
    sale_child=fields.Many2one('sale.order')
    tipo=fields.Char(compute='cliente',store=True)
    oculta=fields.Boolean(store=True)
    estadoRuta=fields.Selection([["borrador","Borrador"],["valido","Confirmado"]],default="borrador")
    reglas=fields.Many2many('stock.warehouse.orderpoint')
    internas=fields.Boolean()
    distribucion=fields.Boolean()
    retiro=fields.Boolean()
    mini=fields.Boolean()
    chofer=fields.Many2one('res.users')
    surtir=fields.Boolean(default=False)

    @api.multi
    def devolucionT(self):
        self.ensure_one()
        action_id = self.env.ref('stock.act_stock_return_picking')
        if(self.sale_id.id):
            pi=self.sale_id.picking_ids.filtered(lambda x:x.date_done!=False and x.state=='done').sorted(key='date_done', reverse=True)
            if(pi!=[]):
                w=self.env['stock.return.picking'].create({'picking_id':pi[0].id,'location_id':12})
                view=self.env.ref('stock.view_stock_return_picking_form')
                for m in self.move_ids_without_package:
                    self.env['stock.return.picking.line'].create({'wizard_id':w.id,'product_id':m.product_id.id,'move_id':m.id,'quantity':m.product_uom_qty})

            #_logger.info(str(pi.mapped('id')))
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




    def ingresoEquiposRetiro(self):
        wiz=self.env['lot.retiro'].create({'pick':self.id})
        for rrr in self.move_ids_without_package:
            ml=self.env['stock.move.line'].search([['move_id','=',rrr.id]])
            if(ml.lot_id.id):
                self.env['lot.retiro.lines'].create({'rel_id':wiz.id,'serie':ml.lot_id.id,'move_id':rrr.id,'move_line':ml.id})
        view = self.env.ref('stock_picking_mass_action.view_lot_retiro')
        return {
            'name': _('Ingreso Series Almacen'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'lot.retiro',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }        


    
    def entregaRefacciones(self):
        wiz = self.env['entrega.action'].create({'pick':self.id,'create_uid':self.env.user.id,'write_uid':self.env.user.id})
        for rrr in self.move_ids_without_package:
            self.env['entrega.refacciones.lines'].create({'product_id':rrr.product_id.id,'cantidadS':rrr.product_uom_qty,'rel_id':wiz.id,'move_id':rrr.id})
        view = self.env.ref('stock_picking_mass_action.view_entrega_refaccion')
        return {
            'name': _('Entrega Refacciones'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'entrega.action',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }

    def validacionZero(self):
        if(self.x_studio_backorder_de==False):
            self.sale_id.action_cancel()
            if(self.sale_id.x_studio_field_bxHgp.stage_id.id!=18 and self.sale_id.x_studio_field_bxHgp.stage_id.id!=3):
                self.sale_id.x_studio_field_bxHgp.write({'stage_id':115})
            self.sale_id.picking_ids.write({'active':False})
            #self.comentario()
        wiz = self.env['comentario.ticket'].create({'pick':self.id,'create_uid':self.env.user.id,'write_uid':self.env.user.id})
        view = self.env.ref('stock_picking_mass_action.view_comentario_ticket')
        return {
            'name': _('Comentario'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'comentario.ticket',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }
    #documentosDistro = fields.Many2many('ir.attachment', string="Evidencias ")
    #historialTicket = fields.One2many('ir.attachment','res_id',string='Evidencias al ticket',store=True,track_visibility='onchange')
    def _log_activity_get_documents(
            self, orig_obj_changes, stream_field, stream, sorted_method=False,
            groupby_method=False):
        """ Avoid error in method:
            env['stock.backorder.confirmation']._process(cancel_backorder=True)
            if mixing complete picking with partial picking and select cancel
            backorder
        """
        if not orig_obj_changes:
            return {}
        else:
            return super()._log_activity_get_documents(
                orig_obj_changes, stream_field, stream,
                sorted_method=sorted_method, groupby_method=groupby_method)

    def regresoAlmacen(self):
        wiz = self.env['devolver.action'].create({'picking':self.id})
        view = self.env.ref('stock_picking_mass_action.view_devolver_action_form')
        return {
            'name': _('Devolver'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'devolver.action',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }

    def devolver(self):
        if(self.ruta_id):
            self.ruta_id=False
            self.estado='Xenrutar'
            wiz = self.env['comentario.ticket'].create({'pick':self.id})
            view = self.env.ref('stock_picking_mass_action.view_comentario_ticket')
            return {
                'name': _('Comentario'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'comentario.ticket',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }


    @api.depends('move_ids_without_package','state')
    def back(self):
        for r in self:
            for rrr in r.move_ids_without_package:
                if(rrr.product_id.categ_id.id==13 and r.state!='done'):
                    r.write({'oculta':True})
                rrrrr=self.env['stock.quant'].search([['product_id','=', rrr.product_id.id],['location_id','=',rrr.location_id.id]]).sorted(key='quantity',reverse=True)
                if(len(rrrrr)==0):
                    r.mensaje="Al confirmar se generara un backorder"


    @api.depends('partner_id')
    def cliente(self):
        for r in self:
            if(r.partner_id):
                if(r.partner_id.state_id):
                    r.tipo=r.partner_id.state_id.name
                    #if(r.partner_id.state_id.code in 'DIF'):
                    #    r.tipo='local'
                    #else:
                    #    r.tipo='foraneo'

    @api.onchange('carrier_tracking_ref')
    def agregarNumeroGuiaATicketOSolicitud(self):
        if(self.sale_id.x_studio_field_bxHgp):
            self.sale_id.x_studio_field_bxHgp.sudo().write({'x_studio_nmero_de_guia_1': self.carrier_tracking_ref})
      
    
    @api.onchange('x_studio_evidencia_a_ticket')
    def mandarTicket(self):
        if(self.sale_id.x_studio_field_bxHgp):
            self.sale_id.x_studio_field_bxHgp.sudo().write({'x_studio_evidencia_distribuidor': self.x_studio_evidencia_a_ticket})
            #c = self.env['helpdesk.ticket'].search([('id','=',self.x_studio_idtempticket)]) 
            #c.write({'x_studio_evidencia_distribuidor': self.x_studio_evidencia_a_ticket})

    @api.onchange('x_studio_comentario_1')
    def mandarTicket(self):
        if(self.sale_id.x_studio_field_bxHgp):
            #c = self.env['helpdesk.ticket'].search([('id','=',self.x_studio_idtempticket)])
            self.env['x_historial_helpdesk'].sudo().create({ 'x_id_ticket' : self.sale_id.x_studio_field_bxHgp.id, 'x_persona' : str(self.env.user.name), 'x_estado' : "Comentario", 'x_disgnostico':self.x_studio_comentario_1}) 
            #c.write({'x_studio_evidencia_distribuidor': self.x_studio_evidencia_a_ticket})

    #@api.onchange('carrier_tracking_ref')
    #def mandarTicketGuia(self):
    #    c = self.env['helpdesk.ticket'].search([('id','=',self.x_studio_idtempticket)]) 
    #    c.write({'x_studio_nmero_de_guia_1': self.carrier_tracking_ref})        
    
    @api.multi
    def button_validate(self):
        self.ensure_one()
        if not self.move_lines and not self.move_line_ids:
            raise UserError(_('Please add some items to move.'))

        # If no lots when needed, raise error
        picking_type = self.picking_type_id
        if(picking_type.id==2 and self.x_studio_evidencia_a_ticket==False):
            raise UserError(_('Se requiere la Evidencia.'))
            
        precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        no_quantities_done = all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in self.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
        no_reserved_quantities = all(float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in self.move_line_ids)
        if no_reserved_quantities and no_quantities_done:
            raise UserError(_('You cannot validate a transfer if no quantites are reserved nor done. To force the transfer, switch in edit more and encode the done quantities.'))
   
        if(self.picking_type_id.id==2 and len(self.x_studio_evidencia)>0):
           if(self.sale_id.x_studio_field_bxHgp):
               self.sale_id.x_studio_field_bxHgp.write({'stage_id':18})
               for ev in self.x_studio_evidencia:
                   self.sale_id.x_studio_field_bxHgp.write({'documentosTecnico':[ev.x_foto]})
                   self.env['x_historial_helpdesk'].sudo().create({ 'x_id_ticket' : self.sale_id.x_studio_field_bxHgp.id
                                                                      , 'x_persona' : str(self.env.user.name)
                                                                      , 'x_estado' : "Cierre"
                                                                      , 'x_disgnostico':ev.x_comentario                                                                   
                                                                     })
                    

        if picking_type.use_create_lots or picking_type.use_existing_lots:
            lines_to_check = self.move_line_ids
            if not no_quantities_done:
                lines_to_check = lines_to_check.filtered(
                    lambda line: float_compare(line.qty_done, 0,
                                               precision_rounding=line.product_uom_id.rounding)
                )

            for line in lines_to_check:
                product = line.product_id
                if product and product.tracking != 'none':
                    if not line.lot_name and not line.lot_id:
                        raise UserError(_('You need to supply a Lot/Serial number for product %s.') % product.display_name)

        if no_quantities_done:
            view = self.env.ref('stock.view_immediate_transfer')
            wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, self.id)]})
            return {
                'name': _('Immediate Transfer?'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.immediate.transfer',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

        if self._get_overprocessed_stock_moves() and not self._context.get('skip_overprocessed_check'):
            view = self.env.ref('stock.view_overprocessed_transfer')
            wiz = self.env['stock.overprocessed.transfer'].create({'picking_id': self.id})
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.overprocessed.transfer',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

        # Check backorder should check for other barcodes
        if self._check_backorder():
            #self.backorder="Parcial"
            if(self.picking_type_id.id==3 or self.picking_type_id.id==29314):
                if(self.sale_id.x_studio_field_bxHgp):
                    self.sale_id.x_studio_field_bxHgp.write({'stage_id':109})
            return self.action_generate_backorder_wizard()
        self.sudo().action_done()
        return            
    
    #@api.one
    @api.depends('estado')
    def x_historial_ticket_actualiza(self):
        for record in self:
            if('SU' in record.name):
                record['value2'] = 1
        #if(self.picking_type_id.id==3 and self.state=="assigned"):
        #    self.value2= 1
        #for record in self:
        #    if((record.picking_type_id.id==3 or record.picking_type_id.id==29314) and record.state=="assigned"):
        #        record['value2']= 1
        #        _logger.info("h")
            # if(record.backorder==False):
            #     record['backorder']=''
            #     self.env.cr.execute("update stock_picking set backorder='' where id ="+str(record.id)+";")
            # if(record.state!=False and record.picking_type_id!=False):
            #     if('assigned' not in record.backorder and (record.picking_type_id.id!=3 or record.picking_type_id.id!=29314) and record.state=='assigned'):
            #        record.write({'estado':'assigned'})
            #        tmp=record.backorder+'assigned'
            #        record.write({'backorder':tmp})
            #     if('cancel' not in record.backorder and record.state=="cancel"):
            #        record.write({'estado':'cancel'})
            #        tmp=record.backorder+'cancel'
            #        record.write({'backorder':tmp})
            #     if('draft' not in record.backorder and record.state=="draft"):
            #        record.write({'estado':'draft'})
            #        tmp=record.backorder+'cancel'
            #        record.write({'backorder':tmp})
            #     if('waiting' not in record.backorder and record.state=="waiting"):
            #         record.write({'estado':'waiting'})
            #         if(record.picking_type_id.id==3 or record.picking_type_id.id==29314):
            #             if(record.sale_id.x_studio_field_bxHgp):
            #                record.sale_id.x_studio_field_bxHgp.write({'stage_id':93})
            #                self.env['x_historial_helpdesk'].sudo().create({ 'x_id_ticket' : record.sale_id.x_studio_field_bxHgp.id, 'x_persona' : str(self.env.user.name), 'x_estado' : "Almacen", 'x_disgnostico':''})
            #         tmp=record.backorder+'waiting'
            #         record.write({'backorder':tmp})                    
            #     if('assigned' not in record.backorder and (record.picking_type_id.id==3 or record.picking_type_id.id==29314) and record.state=="assigned"):
            #         if(record.sale_id.x_studio_field_bxHgp):
            #             record.sale_id.x_studio_field_bxHgp.write({'stage_id':93})
            #             self.env['x_historial_helpdesk'].sudo().create({ 'x_id_ticket' : record.sale_id.x_studio_field_bxHgp.id, 'x_persona' : str(self.env.user.name), 'x_estado' : "Almacen", 'x_disgnostico':''})
            #         self.env.cr.execute("update stock_picking set estado='assigned' where id ="+str(record.id)+";")
            #         if(record.picking_type_id==3):
            #             record['value2']= 1
            #         record.write({'estado':'assigned'})
            #         record.sale_id.x_studio_field_bxHgp.write({'stage_id':93})
            #         tmp=record.backorder+'assigned'
            #         record.write({'backorder':tmp})
            #     if('confirmed' not in record.backorder and (record.picking_type_id.id==3 or record.picking_type_id.id==29314) and record.state=="confirmed"):
            #         record.write({'estado':'confirmed'})
            #         tmp=record.backorder+'confirmed'
            #         record.write({'backorder':tmp})                    
            #     if('aDistribucion' not in record.backorder and "done"==record.state and record.picking_type_id.id==3 ):
            #         record.write({'estado':'aDistribucion'})
            #         tmp=record.backorder+'aDistribucion'
            #         record.write({'backorder':tmp})                    
            #     if('Xenrutar' not in record.backorder and 'done' in record.state and record.picking_type_id.id==29302):
            #         record.write({'estado':'Xenrutar'})
            #         tmp=record.backorder+'Xenrutar'
            #         record.write({'backorder':tmp})                    
            #         if(record.sale_id.x_studio_field_bxHgp):
            #             record.sale_id.x_studio_field_bxHgp.write({'stage_id':94})
            #             self.env['x_historial_helpdesk'].sudo().create({ 'x_id_ticket' : record.sale_id.x_studio_field_bxHgp.id, 'x_persona' : str(self.env.user.name), 'x_estado' : "Distribución", 'x_disgnostico':''}) 
            #         if(record.sale_id):
            #             d=record.env['stock.picking'].search([['sale_id','=',record.sale_id.id],['picking_type_id','=',3]])
            #             d.write({'estado':'distribucion'})
            #     if('entregado' not in record.backorder and 'done' in record.state and (record.picking_type_id.id==2 or record.picking_type_id.id==29314) and len(record.backorder_ids)==0):
            #         record.write({'estado':'entregado'})
            #         if(record.sale_id.x_studio_field_bxHgp):
            #             record.sale_id.x_studio_field_bxHgp.write({'stage_id':18})
            #             self.env['x_historial_helpdesk'].sudo().create({ 'x_id_ticket' : record.sale_id.x_studio_field_bxHgp.id, 'x_persona' : str(self.env.user.name), 'x_estado' : "Entregado", 'x_disgnostico':''})
            #         tmp=record.backorder+'entregado'
            #         record.write({'backorder':tmp})                    
            #     if('entregado' not in record.backorder and 'done' in record.state and (record.picking_type_id.id==2 or record.picking_type_id.id==29314) and len(record.backorder_ids)>0):
            #         record.write({'estado':'entregado'})
            #         if(record.sale_id.x_studio_field_bxHgp):
            #             record.sale_id.x_studio_field_bxHgp.write({'stage_id':109})
            #             self.env['x_historial_helpdesk'].sudo().create({ 'x_id_ticket' : record.sale_id.x_studio_field_bxHgp.id, 'x_persona' : str(self.env.user.name), 'x_estado' : "Parcial", 'x_disgnostico':''})
            #         tmp=record.backorder+'entregado'
            #         record.write({'backorder':tmp})                    
                #if 'assigned' in record.state and record.location_dest_id.id==9 and record.write_uid.id>2:
                #   self.env['x_historial_helpdesk'].sudo().create({ 'x_id_ticket' : numTicket, 'x_persona' : str(self.env.user.name), 'x_estado' : "Refacción Para Entregar"})
                #if 'done' in record.state and record.location_dest_id.id==9 and record.write_uid.id>2:
                #   self.env['x_historial_helpdesk'].sudo().create({ 'x_id_ticket' : numTicket, 'x_persona' : str(self.env.user.name), 'x_estado' : "Refacción Entregada"})                    
            
    def action_toggle_is_locked(self):
        self.ensure_one()
        # if(self.is_locked==True):
        #     #borrado
        #     if(self.sale_id):
        #         self.lineTemp=[(5,0,0)]
        #         dat=[]
        #         for m in self.move_ids_without_package:
        #             dat.append({'producto':m.product_id.id,'cantidad':m.product_uom_qty,'ubicacion':self.location_id.id,'serieDestino':m.x_studio_serie_destino.id})
        #         self.sudo().lineTemp=dat
        #         for s in self.sale_id.order_line:
        #             self.env.cr.execute("delete from stock_move_line where reference='"+self.name+"';")
        #             self.env.cr.execute("delete from stock_move where origin='"+self.sale_id.name+"';")
        #             self.env.cr.execute("delete from sale_order_line where id="+str(s.id)+";")
        # if(self.is_locked==False):
        #     if(self.sale_id):
        #         self.env.cr.execute("update stock_picking set state='draft' where sale_id="+str(self.sale_id.id)+";")
        #         self.env.cr.execute("select id from stock_picking where sale_id="+str(self.sale_id.id)+";")
        #         pickis=self.env.cr.fetchall()
        #         pick=self.env['stock.picking'].search([['id','in',pickis]])
        #         for li in self.lineTemp:
        #             datos={'order_id':self.sale_id.id,'product_id':li.producto.id,'product_uom':li.producto.uom_id.id,'product_uom_qty':li.cantidad,'name':li.producto.description if(li.producto.description) else '/','price_unit':0.00}
        #             if(li.serieDestino):
        #                 datos['x_studio_field_9nQhR']=li.serieDestino.id,
        #             ss=self.env['sale.order.line'].sudo().create(datos)
        #         for p in pick:
        #             p.action_confirm()
        self.is_locked = not self.is_locked
        return True
    
    
    @api.depends('picking_type_id')
    def hide(self):
        for record in self:
            if(record.picking_type_id):
                if('internas' in record.picking_type_id.name or 'Internal' in record.picking_type_id.name):
                    record['hiden']=1
    
    @api.onchange('almacenOrigen')
    def cambioOrigen(self):
        self.location_id=self.almacenOrigen.lot_stock_id.id
    
    @api.onchange('almacenDestino')
    def cambioDestino(self):
        self.location_dest_id=self.almacenDestino.lot_stock_id.id
    
    
    @api.model
    def check_assign_all(self):
        """ Try to assign confirmed pickings """
        domain = [('picking_type_code', '=', 'outgoing'),
                  ('state', '=', 'confirmed')]
        records = self.search(domain, order='scheduled_date')
        records.action_assign()

    def action_immediate_transfer_wizard(self):
        view = self.env.ref('stock.view_immediate_transfer')
        wiz = self.env['stock.immediate.transfer'].create(
            {'pick_ids': [(4, p.id) for p in self]})
        return {
            'name': _('Immediate Transfer?'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.immediate.transfer',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }

    def cambio_wizard(self):
        d=[]
        if(13 in self.move_ids_without_package.mapped('product_id.categ_id.id')):
            wiz = self.env['cambio.toner'].create({'display_name':'h','pick':self.id,'tonerUorden':self.oculta})
        if(13 not in self.move_ids_without_package.mapped('product_id.categ_id.id')):
            wiz = self.env['cambio.toner'].create({'display_name':'h','pick':self.id,'tonerUorden':False})
        for p in self.move_ids_without_package:
            data={'almacen':p.location_id.x_studio_field_JoD2k.id,'move_id':p.id,'rel_cambio':wiz.id,'producto1':p.product_id.id,'producto2':p.product_id.id,'cantidad2':p.product_uom_qty,'cantidad':p.product_uom_qty,'serie':p.x_studio_serie_destino.id,'tipo':self.picking_type_id.id}
            self.env['cambio.toner.line'].create(data)
            #d.append(data)
        
        view = self.env.ref('stock_picking_mass_action.view_cambio_toner_action_form')
        return {
            'name': _('Cambio'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'cambio.toner',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }
    def asignacion_wizard(self):
        d=[]
        wiz = self.env['cambio.toner'].create({'display_name':'h','pick':self.id,'tonerUorden':self.oculta})
        for p in self.move_ids_without_package.filtered(lambda x:x.product_id.categ_id.id==13):
            data={'estado':p.sale_line_id.x_studio_estado,'move_id':p.id,'almacen':self.location_id.x_studio_field_JoD2k.id,'estado':p.sale_line_id.x_studio_estado,'rel_cambio':wiz.id,'producto1':p.product_id.id,'producto2':p.product_id.id,'cantidad':p.product_uom_qty,'cantidad2':p.product_uom_qty,'serie':p.x_studio_serie_destino.id,'tipo':self.picking_type_id.id}
            self.env['cambio.toner.line'].create(data)

        for p in self.move_ids_without_package.filtered(lambda x:x.product_id.categ_id.id==5):
            data={'move_id':p.id,'cantidad2':p.product_uom_qty,'almacen':self.location_id.x_studio_field_JoD2k.id,'rel_cambio':wiz.id,'producto1':p.product_id.id,'producto2':p.product_id.id,'cantidad':p.product_uom_qty,'serie':p.x_studio_serie_destino.id,'tipo':self.picking_type_id.id}
            self.env['cambio.toner.line.toner'].create(data)

        for p in self.move_ids_without_package.filtered(lambda x:x.product_id.categ_id.id==11 or x.product_id.categ_id.id==7):
            data={'move_id':p.id,'cantidad2':p.product_uom_qty,'almacen':self.location_id.x_studio_field_JoD2k.id,'rel_cambio':wiz.id,'producto1':p.product_id.id,'producto2':p.product_id.id,'cantidad':p.product_uom_qty,'serie':p.x_studio_serie_destino.id,'tipo':self.picking_type_id.id}
            self.env['cambio.toner.line.accesorios'].create(data)
        
        view = self.env.ref('stock_picking_mass_action.view_asignacion_equipo_action_form')
        return {
            'name': _('Asignacion'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'cambio.toner',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }
    def guia(self):
        wiz = self.env['guia.ticket'].create({'pick':self.id})
        view = self.env.ref('stock_picking_mass_action.view_guia_ticket')
        return {
            'name': _('Guia'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'guia.ticket',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }
    def comentario(self):
        wiz = self.env['comentario.ticket'].create({'pick':self.id})
        view = self.env.ref('stock_picking_mass_action.view_comentario_ticket')
        return {
            'name': _('Comentario'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'comentario.ticket',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }

    def ingreso(self):
        wiz = self.env['ingreso.almacen'].create({'pick':self.id,'almacen':self.picking_type_id.warehouse_id.id})
        view = self.env.ref('stock_picking_mass_action.view_ingreso_almacen')
        for r in self.move_ids_without_package:
            self.env['ingreso.lines'].create({'move':r.id,'producto':r.product_id.id,'producto2':r.product_id.id,'rel_ingreso':wiz.id,'cantidad':int(r.product_uom_qty)})
        return {
            'name': _('Ingreso'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ingreso.almacen',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }
    def ingresoEquipos(self):
        wiz = self.env['serie.ingreso'].create({'picking':self.id,'almacen':self.picking_type_id.warehouse_id.id})
        view = self.env.ref('stock_picking_mass_action.view_serie_ingreso')
        ml=self.env['stock.move.line'].search([['picking_id','=',self.id]])
        for r in ml:
            if(r.product_id.categ_id.id!=13):
                self.env['serie.ingreso.line'].create({'move_line':r.id,'producto':r.product_id.id,'serie_rel':wiz.id,'cantidad':int(r.product_uom_qty)})
            if(r.product_id.categ_id.id==13):    
                self.env['serie.ingreso.line'].create({'move_line':r.id,'producto':r.product_id.id,'serie_rel':wiz.id,'cantidad':int(1),'categoria':13})
        return {
            'name': _('Ingreso Equipos'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'serie.ingreso',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }

    def serie(self):
        wiz = self.env['picking.serie'].create({'pick':self.id})
        for r in self.move_ids_without_package:
            if(r.product_id.categ_id.id==13):
                 self.env['picking.serie.line'].create({'producto':self.product_id.id,'rel_picki_serie':wiz.id,'move_id':r.id})
        view = self.env.ref('stock_picking_mass_action.view_picking_serie')
        
        return {
            'name': _('Serie'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'picking.serie',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }



    def inter_wizard(self):
        wiz = self.env['transferencia.interna'].create({})
        view = self.env.ref('stock_picking_mass_action.view_transferencia_interna')
        return {
            'name': _('Serie'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'transferencia.interna',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }


    # @api.depends('move_type', 'move_lines.state', 'move_lines.picking_id')
    # @api.one
    # def _compute_state(self):
    #     if not self.move_lines:
    #         self.state = 'draft'
    #         self.estado='draft'
    #     elif any(move.state == 'draft' for move in self.move_lines):  # TDE FIXME: should be all ?
    #         self.state = 'draft'
    #         self.estado='draft'

    #     elif all(move.state == 'cancel' for move in self.move_lines):
    #         self.state = 'cancel'
    #         self.estado='cancel'
    #     elif all(move.state in ['cancel', 'done'] for move in self.move_lines):
    #         self.state = 'done'
    #         if(self.state=='done'):
    #             if(self.picking_type_id.id==3 and self.ajusta!=True):
    #                 self.estado='aDistribucion'
    #                 self.ajusta=True
    #             if(self.picking_type_id.id==29302):
    #                 self.estado='Xenrutar'
    #                 if(self.sale_id):
    #                     d=self.env['stock.picking'].search([['sale_id','=',self.sale_id.id],['picking_type_id','=',3]])
    #                     d.write({'estado':'distribucion'})
    #                     if(self.sale_id.x_studio_field_bxHgp):
    #                         self.sale_id.x_studio_field_bxHgp.stage_id=94 
    #             if((self.picking_type_id.id==2 or self.picking_type_id.id==29314) and len(self.backorder_ids)==0):
    #                 self.estado='entregado'
    #                 if(self.sale_id.x_studio_field_bxHgp):
    #                     self.sale_id.x_studio_field_bxHgp.stage_id=18
    #             if((self.picking_type_id.id==2 or self.picking_type_id.id==29314) and len(self.backorder_ids)>0):
    #                 self.estado='entregado'
    #                 if(self.sale_id.x_studio_field_bxHgp):
    #                     self.sale_id.x_studio_field_bxHgp.stage_id=109 
    #     else:
    #         relevant_move_state = self.move_lines._get_relevant_state_among_moves()
    #         if relevant_move_state == 'partially_available':
    #             self.state = 'assigned'
    #             if(self.picking_type_id.id!=3 and self.ajusta!=True):
    #                 self.estado='assigned'
    #             if(self.picking_type_id.id==3):
    #                 if(self.sale_id.x_studio_field_bxHgp):
    #                     self.sale_id.x_studio_field_bxHgp.stage_id=93
    #                 self.value2= 1
    #                 self.estado='assigned'


    #         else:
    #             self.state = relevant_move_state
    #             self.estado=relevant_move_state
    #             if(self.sale_id.x_studio_field_bxHgp and relevant_move_state=='waiting' and (self.picking_type_id.id==3 or self.picking_type_id.id==29314)):
    #                 self.sale_id.x_studio_field_bxHgp.stage_id=93
    #             if(self.state=="confirmed"):
    #                 self.estado='confirmed'
    @api.multi
    def cierre(self):
        if(self.x_studio_evidencia_a_ticket and self.partner_id.state_id.name in ["Estado de México","Ciudad de México"]):
            #self.sudo().action_done()
            wiz=self.env['stock.picking.mass.action'].create({'picking_ids':[(4,self.id)],'confirm':True,'check_availability':True,'transfer':True})
            _logger.info(str(self.id))
            #obj.mass_action()
            #view_stock_picking_mass_action_form
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
        if(self.partner_id.state_id.name not in ["Estado de México","Ciudad de México"]):
            wiz=self.env['stock.picking.mass.action'].create({'picking_ids':[(4,self.id)],'confirm':True,'check_availability':True,'transfer':True})
            _logger.info(str(self.id))
            #obj.mass_action()
            #view_stock_picking_mass_action_form
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
        else:
           raise UserError(_('Se requiere evidencia'))

class StockPicking(Model):
    _inherit = 'stock.move'
    almacenOrigen=fields.Many2one('stock.warehouse','Almacen Origen')
    
            
    @api.onchange('almacenOrigen')
    def cambioOrigen(self):
        if(self.almacenOrigen):
            self.location_id=self.almacenOrigen.lot_stock_id.id
        
class StockPickingMoveTemp(Model):
    _name='stock.pick.temp'
    _description='Lineas Temporales'
    producto=fields.Many2one('product.product')
    modelo=fields.Char(related='producto.name',string='Modelo')
    noParte=fields.Char(related='producto.default_code',string='No. Parte')
    descripcion=fields.Text(related='producto.description',string='Descripción')
    stock=fields.Many2one('stock.quant',string='Existencia')
    cantidad=fields.Integer('Demanda Inicial')
    almacen=fields.Many2one('stock.warehouse','Almacén Origen')
    ubicacion=fields.Many2one('stock.location','Ubicación')
    disponible=fields.Float(related='stock.quantity')
    picking=fields.Many2one('stock.picking')
    unidad=fields.Many2one('uom.uom',related='producto.uom_id')
    lock=fields.Boolean('lock')
    serieDestino=fields.Many2one('stock.production.lot')
    
    @api.onchange('ubicacion','producto')
    def quant(self):
        self.disponible=0
        h=self.env['stock.quant'].search([['product_id','=',self.producto.id],['location_id','=',self.ubicacion.id],['quantity','>',0]])
        if(len(h)>0):
            self.stock=h.id
        if(len(h)==0):
            d=self.env['stock.location'].search([['location_id','=',self.ubicacion.id]])
            for di in d:
                i=self.env['stock.quant'].search([['product_id','=',self.producto.id],['location_id','=',di.id],['quantity','>',0]])
                if(len(i)>0):
                    self.stock=i.id