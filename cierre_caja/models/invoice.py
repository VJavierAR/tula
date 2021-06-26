from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime

medio_pago_values = [('cheque', 'Cheque'), ('efectivo', 'Efectivo'), ('datafono', 'Datafono Local'), ('transferencia', 'Transferencia')]

class AccountPayment(models.Model):
    _inherit = "account.payment"

    cierre_id = fields.Many2one('cierre.caja')
    incluir = fields.Boolean('Incluir', default=False)
    tipo_pago=fields.Selection([('Contado','Contado'),('Credito','Credito')],default='Credito')

    def get_tipo_pago(self):
        m=[]
        t=self.env['tipo.pago'].search([])
        for ti in t:
            m.append((ti.name,ti.name))
        for a in medio_pago_values:
            m.append(a)
        return m
    
    medio_pago = fields.Selection(get_tipo_pago, string='Medio Pago')



class CierreLineas(models.Model):
    _name = "cierre.caja.lineas"

    name = fields.Many2one('account.journal', 'Diario')
    monto_calculado = fields.Float('Pagos realizados', compute='compute_monto_calculado')
    diferencia = fields.Float('Diferencia', compute='compute_monto_calculado')
    monto_reportado = fields.Float('Monto Reportado')
    cierre_id = fields.Many2one('cierre.caja')
    monto_acumulado= fields.Float('Acumulado', compute='compute_monto_acumulado')
    monto_final= fields.Float('Acumulado', compute='compute_monto_final')

    @api.depends('name')
    def compute_monto_acumulado(self):
        fecha=fields.Datetime.now()
        ayer=datetime(fecha.year, fecha.month, fecha.day)
        prime_day_of_month=datetime(fecha.year, fecha.month, 1)
        last_date_of_month = datetime(fecha.year, fecha.month, 1) + relativedelta(months=1, days=-1)
        acunt=self.env['account.payment'].search([['journal_id','=',self.name.id],['payment_date','>=',prime_day_of_month],['payment_date','<',ayer]])  
        self.monto_acumulado=sum(acunt.mapped('amount'))

    @api.depends('name')
    def compute_monto_calculado(self):
        if not len(self.ids):
            return True
        
        for line in self:
            pagos = line.cierre_id.pagos_hoy
            line.monto_calculado = sum(pagos.filtered(lambda p: p.journal_id == line.name).mapped('amount'))
            line.diferencia = line.monto_calculado - line.monto_reportado
    
    @api.depends('name')
    def compute_monto_final(self):
        self.monto_final=self.monto_calculado+self.monto_acumulado

class CierreLineas2(models.Model):
    _name = "cierre.caja.lineas2"

    name = fields.Char('Medio Pago')
    internal_name = fields.Char('Medio Pago')
    monto_calculado = fields.Float('Pagos realizados', compute='compute_monto_calculado')
    diferencia = fields.Float('Diferencia', compute='compute_monto_calculado')
    monto_reportado = fields.Float('Monto Reportado')
    cierre_id = fields.Many2one('cierre.caja')

    @api.depends('name')
    def compute_monto_calculado(self):
        if not len(self.ids):
            return True
        
        
        for line in self:
            pagos = line.cierre_id.pagos_hoy
            line.monto_calculado = sum(pagos.filtered(lambda p: p.medio_pago == line.internal_name and p.payment_type=='inbound').mapped('amount'))-sum(pagos.filtered(lambda p: p.medio_pago == line.internal_name and p.payment_type=='outbound').mapped('amount'))
            line.diferencia = line.monto_calculado - line.monto_reportado

class Cierre(models.Model):
    _name = "cierre.caja"

    """
    @api.depends('name')
    def compute_pagos_hoy(self):
        for cierre in self:
            hoy = cierre.name
            inicio_dia = hoy.replace(hour=0, minute=0, second=0)
            cierre_dia = hoy.replace(hour=23, minute=59, second=59)
            pagos = self.env['account.payment'].search(
                [('create_date', '>=', inicio_dia), ('create_date', '<=', cierre_dia)])
            cierre.pagos_hoy =  pagos
    """
    
    @api.depends('desglose_pagos2')
    def compute_monto_cierre_calculado(self):
        for cierre in self:
            total_pagos = sum(cierre.desglose_pagos2.mapped('monto_calculado'))
            monto_reportado = sum(cierre.desglose_pagos2.mapped('monto_reportado'))
            cierre.update(dict(monto_cierre_calculado = total_pagos , monto_cierre=monto_reportado,monto_cierre_sin=(total_pagos+cierre.monto_apertura)))

    @api.depends('monto_cierre_calculado', 'monto_cierre')
    def compute_diferencia(self):
        for cierre in self:
            if cierre.state == 'draft':
                cierre.diferencia = 0
            else:
                cierre.diferencia = cierre.monto_cierre_calculado - cierre.monto_cierre
                
    @api.onchange('user_id')
    def calcular_apertura(self):
        if self.user_id:
            conf_usuario = self.env["cierre.conf"].search([('user_id', '=', self.user_id.id)], limit=1)
            if conf_usuario:
                self.monto_apertura = conf_usuario.monto_inicio
            else:
                self.monto_apertura = self.env['ir.config_parameter'].sudo().get_param('cierre_caja.monto_apertura', 50000)
            
    state = fields.Selection([('draft', 'Borrador'), ('progress', 'En proceso'), ('closed', 'Cerrada')], string='Estado', default='draft')
    name = fields.Datetime('Fecha Inicio', required=True, default=fields.Datetime.now)
    date_closed = fields.Datetime('Fecha de cierre')
    monto_apertura = fields.Float('Monto apertura')
    monto_cierre_calculado = fields.Float('Cierre estimado calculado', compute='compute_monto_cierre_calculado')
    monto_cierre = fields.Float('Monto Cierre', compute='compute_monto_cierre_calculado')
    diferencia = fields.Float('Diferencia', compute='compute_diferencia')
    desglose_pagos = fields.One2many('cierre.caja.lineas', 'cierre_id')
    desglose_pagos2 = fields.One2many('cierre.caja.lineas2', 'cierre_id')
    user_id = fields.Many2one('res.users', copy=False,
                                      string='Usuario',
                                      default=lambda self: self.env.user)

    pagos_hoy = fields.One2many('account.payment', 'cierre_id', domain=[('incluir', '=', True)])
    pagos_hoy_olvidados = fields.One2many('account.payment', 'cierre_id', domain=[('incluir', '=', False)])

    notas = fields.Text('Notas')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    monto_cierre_acumulado=fields.Float('Monto Cierre Acumulado',compute='compute_monto_cierre_acumulado')
    monto_cierre_sin=fields.Float()

    def compute_monto_cierre_acumulado(self):
        fecha=fields.Datetime.now()
        prime_day_of_month=datetime(fecha.year, fecha.month, 1)
        last_date_of_month = datetime(fecha.year, fecha.month, 1) + relativedelta(months=1, days=-1)
        data=self.search([['name','>=',prime_day_of_month],['name','<=',last_date_of_month],['user_id','=',self.user_id.id]])
        self.monto_cierre_acumulado=sum(data.mapped('diferencia'))


    def print_report(self):
        return self.env.ref('cierre_caja.cierre_caja_report').report_action(self)

    def set_progress(self):
        jounal_env = self.env['account.journal']
        for cierre in self:
            vals = dict(state='progress')
            journal_ids = jounal_env.search([('type', 'in', ('bank', 'cash')),('quitar_diario','=',False)])
            vals['desglose_pagos'] = []
            vals['desglose_pagos2'] = []
            for j in journal_ids:
                vals['desglose_pagos'].append((0, 0, {'name': j.id, 'cierre_id': cierre.id}))
            for m in medio_pago_values:
                vals['desglose_pagos2'].append((0, 0, {'name': m[1], 'internal_name': m[0], 'cierre_id': cierre.id}))
            cierre.write(vals)

    def set_closed(self):
        fecha=fields.Datetime.now()
        last_date_of_month = datetime(fecha.year, fecha.month, 1) + relativedelta(months=1, days=-1)
        for cierre in self:
            if(fecha.day==last_date_of_month.day):
                if(cierre.monto_cierre_acumulado!=0):
                    raise UserError('No se puede cerrar la caja tiene una diferencia de '+str(cierre.monto_cierre_acumulado))
                else:
                    cierre.write({'state': 'closed', 'date_closed': fields.Datetime.now()})
            else:
                cierre.write({'state': 'closed', 'date_closed': fields.Datetime.now()})
    def get_payments(self):
        payment_env = self.env['account.payment']
        for cierre in self:

            inicio_dia = cierre.name
            #inicio_dia = hoy.replace(hour=0, minute=0, second=0)
            cierre_dia = fields.Datetime.now()

            pagos = payment_env.search(
                [('create_date', '>=', cierre.name), ('create_date', '<=', cierre_dia), ('create_uid', '=', cierre.user_id.id), ('state', 'not in', ('draft', 'cancelled')), ('partner_type', '=', 'customer'), ('payment_type', 'in', ('inbound', 'outbound')),('journal_id.quitar_diario','=',False)])
            #pagos |= payment_env.search(
            #    [('create_date', '>=', '2020-08-10 00:00:00'), ('create_date', '<=', inicio_dia), ('create_uid', '=', cierre.user_id.id), ('incluir', '=', True)])
            #pagos_hoy_olvidados = payment_env.search(
            #    [('create_date', '>=', '2020-08-10 00:00:00'), ('create_date', '<=', inicio_dia), ('create_uid', '=', cierre.user_id.id), ('incluir', '=', False)])
            if pagos:
                todos_pagos = pagos
                #todos_pagos |= pagos_hoy_olvidados
                todos_pagos.write({'cierre_id': cierre.id, 'incluir': False})
                pagos.write({'incluir': True})

                cierre.write({'pagos_hoy': pagos,}) # 'pagos_hoy_olvidados': pagos_hoy_olvidados})

    def dummy_bottom(self):

        self.desglose_pagos.compute_monto_calculado()
        self.desglose_pagos2.compute_monto_calculado()
        return True

    @api.model
    def create(self, vals):
        if self.search([('create_uid', '=', self.env.user.id), ('state', '=', 'progress')]):
            raise UserError('No puede abrir otra caja ya que usted tiene una caja abierta')
        return super(Cierre, self).create(vals)

    def unlink(self):
        for cierre in self:
            if cierre.state != 'draft':
                raise UserError('No puede eliminar el ciere %s ya que no está en borrador'% (cierre.name_get()[0][1],))
        return super(Cierre, self).unlink()
    
    def get_pagos(self):
        fecha=fields.Datetime.now()
        ayer=datetime(fecha.year, fecha.month, fecha.day)
        prime_day_of_month=datetime(fecha.year, fecha.month, 1)
        last_date_of_month = datetime(fecha.year, fecha.month, 1) + relativedelta(months=1, days=-1)
        acumulado=self.env['account.payment'].search([['payment_date','>=',prime_day_of_month],['payment_date','<',ayer]])
        hoy=self.env['account.payment'].search([['payment_date','=',fecha]])
        data=[]
        data.append(['Contado',sum(acumulado.filtered(lambda x:x.tipo_pago=='Contado').mapped('amount')),sum(hoy.filtered(lambda x:x.tipo_pago=='Contado').mapped('amount')),sum(acumulado.filtered(lambda x:x.tipo_pago=='Contado').mapped('amount'))+sum(hoy.filtered(lambda x:x.tipo_pago=='Contado').mapped('amount'))])
        data.append(['Abonos Recibidos',sum(acumulado.filtered(lambda x:x.tipo_pago=='Credito').mapped('amount')),sum(hoy.filtered(lambda x:x.tipo_pago=='Credito').mapped('amount')),sum(acumulado.filtered(lambda x:x.tipo_pago=='Credito').mapped('amount'))+sum(hoy.filtered(lambda x:x.tipo_pago=='Credito').mapped('amount'))])
        data.append(['Total Depositos',sum(acumulado.filtered(lambda x:x.tipo_pago=='Contado').mapped('amount'))+sum(acumulado.filtered(lambda x:x.tipo_pago=='Credito').mapped('amount')),sum(hoy.filtered(lambda x:x.tipo_pago=='Contado').mapped('amount'))+sum(hoy.filtered(lambda x:x.tipo_pago=='Credito').mapped('amount')),sum(acumulado.filtered(lambda x:x.tipo_pago=='Contado').mapped('amount'))+sum(acumulado.filtered(lambda x:x.tipo_pago=='Credito').mapped('amount'))+sum(hoy.filtered(lambda x:x.tipo_pago=='Contado').mapped('amount'))+sum(hoy.filtered(lambda x:x.tipo_pago=='Credito').mapped('amount'))])
        return data



    def get_facturas(self):
        fecha=fields.Datetime.now()
        ayer=datetime(fecha.year, fecha.month, fecha.day)
        prime_day_of_month=datetime(fecha.year, fecha.month, 1)
        last_date_of_month = datetime(fecha.year, fecha.month, 1) + relativedelta(months=1, days=-1)
        acumulado=self.env['account.move'].search([['invoice_date','>=',prime_day_of_month],['invoice_date','<',ayer],['type','=','out_invoice']])
        hoy=self.env['account.move'].search([['invoice_date','=',fecha],['type','=','out_invoice']])
        data=[]
        inmediato=self.env.ref('account.account_payment_term_immediate')
        #credito_hoy=
        #contado_hoy=
        #credito_acumulado=
        #contado_acumulado=
        data.append(['Ventas Contado',sum(acumulado.filtered(lambda x:x.invoice_payment_term_id.id==inmediato.id).mapped('amount_total')),sum(hoy.filtered(lambda x:x.invoice_payment_term_id.id==inmediato.id).mapped('amount_total')),sum(acumulado.filtered(lambda x:x.invoice_payment_term_id.id==inmediato.id).mapped('amount_total'))+sum(hoy.filtered(lambda x:x.invoice_payment_term_id.id==inmediato.id).mapped('amount_total'))])
        data.append(['Ventas Credito',sum(acumulado.filtered(lambda x:x.invoice_payment_term_id.id!=inmediato.id).mapped('amount_total')),sum(hoy.filtered(lambda x:x.invoice_payment_term_id.id!=inmediato.id).mapped('amount_total')),sum(acumulado.filtered(lambda x:x.invoice_payment_term_id.id!=inmediato.id).mapped('amount_total'))+sum(hoy.filtered(lambda x:x.invoice_payment_term_id.id!=inmediato.id).mapped('amount_total'))])
        data.append(['Total Ventas',sum(acumulado.filtered(lambda x:x.invoice_payment_term_id.id!=inmediato.id).mapped('amount_total'))+sum(acumulado.filtered(lambda x:x.invoice_payment_term_id.id==inmediato.id).mapped('amount_total')),sum(hoy.filtered(lambda x:x.invoice_payment_term_id.id!=inmediato.id).mapped('amount_total'))+sum(acumulado.filtered(lambda x:x.invoice_payment_term_id.id==inmediato.id).mapped('amount_total')),sum(acumulado.filtered(lambda x:x.invoice_payment_term_id.id!=inmediato.id).mapped('amount_total'))+sum(hoy.filtered(lambda x:x.invoice_payment_term_id.id!=inmediato.id).mapped('amount_total'))+sum(acumulado.filtered(lambda x:x.invoice_payment_term_id.id==inmediato.id).mapped('amount_total'))+sum(hoy.filtered(lambda x:x.invoice_payment_term_id.id==inmediato.id).mapped('amount_total'))])
        return data

    def get_ventas(self):
        fecha=fields.Datetime.now()
        ayer=datetime(fecha.year, fecha.month, fecha.day)
        prime_day_of_month=datetime(fecha.year, fecha.month, 1)
        last_date_of_month = datetime(fecha.year, fecha.month, 1) + relativedelta(months=1, days=-1)
        hoy_temp=fecha+relativedelta(days=1)
        hoy=datetime(hoy_temp.year, hoy_temp.month, hoy_temp.day)
        lines=self.env['sale.order.line'].search([['state','=','sale'],['write_date','>=',prime_day_of_month],['write_date','<',ayer]])
        total=0
        descuento=0
        iva=0
        total2=0
        descuento2=0
        iva2=0
        for li in lines:
            total=total+(li.price_unit*li.product_uom_qty)
            descuento=descuento+((li.price_unit*li.product_uom_qty)-(li.price_subtotal*li.product_uom_qty))
            iva=iva+(li.price_tax*li.product_uom_qty)
        lines2=self.env['sale.order.line'].search([['state','=','sale'],['write_date','>',ayer],['write_date','<',hoy]])
        for li in lines2:
            total2=total2+(li.price_unit*li.product_uom_qty)
            descuento2=descuento2+((li.price_unit*li.product_uom_qty)-(li.price_subtotal*li.product_uom_qty))
            iva2=iva2+(li.price_tax*li.product_uom_qty)
        data=[]
        data.append(['Ventas',total,total2,total+total2])
        data.append(['Descuento',descuento,descuento2,descuento+descuento2])
        data.append(['Impuestos',iva,iva2,iva+iva2])
        data.append(['Total',total-descuento+iva,total2-descuento2+iva2,total-descuento+iva+(total2-descuento2+iva2)])
        return data
class CierreConf(models.Model):
    _name = "cierre.conf"

    user_id = fields.Many2one('res.users', 'Usuario', required=1)
    journal_ids = fields.Many2many('account.journal', string='Diarios')
    monto_inicio = fields.Float('Monto Inicio caja')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    

