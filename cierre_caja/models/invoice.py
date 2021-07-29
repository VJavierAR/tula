from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime
import logging, ast
_logger = logging.getLogger(__name__)


medio_pago_values = [('cheque', 'Cheque'), ('efectivo', 'Efectivo'), ('datafono', 'Datafono Local'), ('transferencia', 'Transferencia')]

class AccountPayment(models.Model):
    _inherit = "account.payment"

    cierre_id = fields.Many2one('cierre.caja')
    incluir = fields.Boolean('Incluir', default=False)
    tipo_pago=fields.Selection([('Contado','Contado'),('Credito','Credito')],default='Credito')
    monto_moneda=fields.Float('Monto')

    @api.onchange('currency_id')
    def actulizaMonneda(self):
        for rec in self:
            rec.monto_moneda=rec.amount if(rec.payment_type!='outbound') else -rec.amount
            moneda=self.company_id.currency_id.id
            if(rec.currency_id.id!=moneda):
                rec.monto_moneda=(rec.amount/rec.currency_id.rate) if(rec.payment_type!='outbound') else -(rec.amount/rec.currency_id.rate)

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
        for record in self:
            acunt=self.env['account.payment'].search([['journal_id','=',record.name.id],['payment_date','>=',prime_day_of_month],['payment_date','<',ayer]])  
            record.monto_acumulado=sum(acunt.mapped('amount'))

    @api.depends('name')
    def compute_monto_calculado(self):
        if not len(self.ids):
            return True
        
        for line in self:
            pagos = line.cierre_id.pagos_hoy
            line.monto_calculado = sum(pagos.filtered(lambda p: p.journal_id == line.name).mapped('monto_moneda'))
            line.diferencia = line.monto_calculado - line.monto_reportado
    
    @api.depends('name')
    def compute_monto_final(self):
        for record in self:
            record.monto_final=record.monto_calculado+record.monto_acumulado

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
            line.monto_calculado = sum(pagos.filtered(lambda p: p.medio_pago == line.internal_name and p.payment_type=='inbound').mapped('monto_moneda'))-sum(pagos.filtered(lambda p: p.medio_pago == line.internal_name and p.payment_type=='outbound').mapped('monto_moneda'))
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
                cierre.diferencia = round((cierre.monto_cierre_calculado - cierre.monto_cierre),2)
                
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
    monto_cierre_diferencia=fields.Float('Monto abonar')

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
        tresdiasmenos=self.name+relativedelta(days=-3)
        inmediato=self.env.ref('account.account_payment_term_immediate')
        facturas=self.env['account.move'].search([['invoice_date','<',tresdiasmenos],['invoice_payment_term_id','=',inmediato.id],['amount_residual_signed','!=',0],['state','=','posted'],['type','=','out_invoice']])
        for cierre in self:
            if(facturas.mapped('id')!=[]):
                raise UserError('No se puede cerrar dado que existen facturas de contado sin pagar: '+str(facturas.mapped('name')).replace('[','').replace(']',''))
            if(fecha.day==last_date_of_month.day):
                if(cierre.monto_cierre_acumulado!=0):
                    raise UserError('No se puede cerrar la caja tiene una diferencia de '+str(cierre.monto_cierre_acumulado))
                else:
                    cierre.write({'state': 'closed', 'date_closed': fields.Datetime.now()})
            if(cierre.diferencia-cierre.monto_cierre_diferencia>0):
                raise UserError('No se puede cerrar la caja tiene una diferencia de '+str(cierre.diferencia))
            if(cierre.diferencia-cierre.monto_cierre_diferencia<=0):
                cierre.write({'state': 'closed', 'date_closed': fields.Datetime.now()})

    def get_payments(self):
        payment_env = self.env['account.payment']
        for cierre in self:

            inicio_dia = cierre.name
            #inicio_dia = hoy.replace(hour=0, minute=0, second=0)
            cierre_dia = fields.Datetime.now()

            pagos = payment_env.search(
                [('create_date', '>=', cierre.name), ('create_date', '<=', cierre_dia), ('create_uid', '=', cierre.user_id.id), ('state', 'not in', ('draft', 'cancelled')), ('partner_type', '=', 'customer'), ('payment_type', 'in', ('inbound', 'outbound')),('journal_id.quitar_diario','=',False)])
            for p in pagos.filtered(lambda x:x.monto_moneda==0):
                p.actulizaMonneda()
            #pagos |= payment_env.search(
            #    [('create_date', '>=', '2020-08-10 00:00:00'), ('create_date', '<=', inicio_dia), ('create_uid', '=', cierre.user_id.id), ('incluir', '=', True)])
            #pagos_hoy_olvidados = payment_env.search(
            #    [('create_date', '>=', '2020-08-10 00:00:00'), ('create_date', '<=', inicio_dia), ('create_uid', '=', cierre.user_id.id), ('incluir', '=', False)])
            if pagos:
                todos_pagos = pagos
                m=payment_env.search([['cierre_id','=',cierre.id]])
                if(len(m)>0):
                    m.write({'cierre_id':False,'incluir':False})
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
        fecha=self.name
        ayer=datetime(fecha.year, fecha.month, fecha.day)
        prime_day_of_month=datetime(fecha.year, fecha.month, 1)
        last_date_of_month = datetime(fecha.year, fecha.month, 1) + relativedelta(months=1, days=-1)
        acumulado=self.env['account.payment'].search([['payment_date','>=',prime_day_of_month],['payment_date','<',ayer]])
        hoy=self.env['account.payment'].search([['payment_date','=',fecha]])
        acumulado=acumulado.filtered(lambda x:x.payment_type!='outbound')
        hoy=hoy.filtered(lambda x:x.payment_type!='outbound')
        data=[]
        data.append(['Contado',"{0:.2f}".format(sum(acumulado.filtered(lambda x:x.tipo_pago=='Contado').mapped('monto_moneda'))),"{0:.2f}".format(sum(hoy.filtered(lambda x:x.tipo_pago=='Contado').mapped('monto_moneda'))),"{0:.2f}".format(sum(acumulado.filtered(lambda x:x.tipo_pago=='Contado').mapped('monto_moneda'))+sum(hoy.filtered(lambda x:x.tipo_pago=='Contado').mapped('monto_moneda')))])
        data.append(['Abonos Recibidos',"{0:.2f}".format(sum(acumulado.filtered(lambda x:x.tipo_pago=='Credito').mapped('monto_moneda'))),"{0:.2f}".format(sum(hoy.filtered(lambda x:x.tipo_pago=='Credito').mapped('monto_moneda'))),"{0:.2f}".format(sum(acumulado.filtered(lambda x:x.tipo_pago=='Credito').mapped('monto_moneda'))+sum(hoy.filtered(lambda x:x.tipo_pago=='Credito').mapped('monto_moneda')))])
        data.append(['Total Depositos',"{0:.2f}".format(sum(acumulado.filtered(lambda x:x.tipo_pago=='Contado').mapped('monto_moneda'))+sum(acumulado.filtered(lambda x:x.tipo_pago=='Credito').mapped('monto_moneda'))),"{0:.2f}".format(sum(hoy.filtered(lambda x:x.tipo_pago=='Contado').mapped('monto_moneda'))+sum(hoy.filtered(lambda x:x.tipo_pago=='Credito').mapped('monto_moneda'))),"{0:.2f}".format(sum(acumulado.filtered(lambda x:x.tipo_pago=='Contado').mapped('monto_moneda'))+sum(acumulado.filtered(lambda x:x.tipo_pago=='Credito').mapped('monto_moneda'))+sum(hoy.filtered(lambda x:x.tipo_pago=='Contado').mapped('monto_moneda'))+sum(hoy.filtered(lambda x:x.tipo_pago=='Credito').mapped('monto_moneda')))])
        return data



    def get_facturas(self):
        fecha=self.name
        ayer=datetime(fecha.year, fecha.month, fecha.day)
        prime_day_of_month=datetime(fecha.year, fecha.month, 1)
        last_date_of_month = datetime(fecha.year, fecha.month, 1) + relativedelta(months=1, days=-1)
        acumulado=self.env['account.move'].search([['invoice_date','>=',prime_day_of_month],['invoice_date','<',ayer],['type','=','out_invoice']])
        hoy=self.env['account.move'].search([['invoice_date','=',fecha],['type','=','out_invoice']])
        notas_acumulado=self.env['account.move'].search([['invoice_date','>=',prime_day_of_month],['invoice_date','<',ayer],['type','=','out_refund']])
        notas_hoy=self.env['account.move'].search([['invoice_date','=',fecha],['type','=','out_refund']])
        data=[]
        inmediato=self.env.ref('account.account_payment_term_immediate')
        contado_ayer=sum(acumulado.filtered(lambda x:x.invoice_payment_term_id.id==inmediato.id).mapped('amount_total_signed'))
        contado_hoy=sum(acumulado.filtered(lambda x:x.invoice_payment_term_id.id==inmediato.id).mapped('amount_total_signed'))
        credito_ayer=sum(acumulado.filtered(lambda x:x.invoice_payment_term_id.id!=inmediato.id).mapped('amount_total_signed'))
        credito_hoy=sum(hoy.filtered(lambda x:x.invoice_payment_term_id.id!=inmediato.id).mapped('amount_total_signed'))
        notas_ayer=sum(notas_acumulado.mapped('amount_total_signed'))
        notas_hoy1=sum(notas_hoy.mapped('amount_total_signed'))
        data.append(['Ventas Contado',"{0:.2f}".format(contado_ayer),"{0:.2f}".format(contado_hoy),"{0:.2f}".format(contado_ayer+contado_hoy)])
        data.append(['Ventas Credito',"{0:.2f}".format(credito_ayer),"{0:.2f}".format(credito_hoy),"{0:.2f}".format(credito_ayer+credito_hoy)])
        data.append(['Notas Credito',"{0:.2f}".format(notas_ayer),"{0:.2f}".format(notas_hoy1),"{0:.2f}".format(notas_hoy1+notas_ayer)])
        data.append(['Total Ventas',"{0:.2f}".format(contado_ayer+credito_ayer+notas_ayer),"{0:.2f}".format(contado_hoy+credito_hoy+notas_hoy1),"{0:.2f}".format(contado_ayer+credito_ayer+notas_ayer+contado_hoy+credito_hoy+notas_hoy1)])
        return data

    def get_ventas(self):
        fecha=self.name
        ayer=datetime(fecha.year, fecha.month, fecha.day)
        prime_day_of_month=datetime(fecha.year, fecha.month, 1)
        last_date_of_month = datetime(fecha.year, fecha.month, 1) + relativedelta(months=1, days=-1)
        hoy_temp=fecha+relativedelta(days=1)
        hoy=datetime(hoy_temp.year, hoy_temp.month, hoy_temp.day)
        lines=self.env['account.move'].search(['&','&','&',['invoice_date','>=',prime_day_of_month],['invoice_date','<',ayer],['state','=','posted'],['type','=','out_invoice']])
        total=0
        descuento=0
        iva=0
        total2=0
        descuento2=0
        iva2=0
        moneda=self.env.user.company_id.currency_id.id
        _logger.info(str(moneda))
        for li in lines:
            for liin in li.invoice_line_ids:
                total=total+(liin.price_unit*liin.quantity)
                _logger.info(str(liin.currency_id.id))
                if(liin.currency_id.id!=moneda and liin.currency_id.id!=False):
                    descuento=descuento+(((liin.price_unit*liin.quantity)-(liin.price_subtotal))/liin.currency_id.rate)
                else:
                    descuento=descuento+((liin.price_unit*liin.quantity)-(liin.price_subtotal))
            iva=iva+(li.amount_total_signed-li.amount_untaxed_signed)
        lines2=self.env['account.move'].search(['&','&',['invoice_date','=',fecha],['state','=','posted'],['type','=','out_invoice']])
        for li in lines2:
            for liin in li.invoice_line_ids:
                total2=total2+(liin.price_unit*liin.quantity)
                if(liin.currency_id.id!=moneda and liin.currency_id.id!=False):
                    descuento2=descuento2+(((liin.price_unit*liin.quantity)-(liin.price_subtotal))/liin.currency_id.rate)                    
                else:
                    descuento2=descuento2+((liin.price_unit*liin.quantity)-(liin.price_subtotal))
            iva2=iva2+(li.amount_total_signed-li.amount_untaxed_signed)
        data=[]
        data.append(['Ventas',"{0:.2f}".format(total),"{0:.2f}".format(total2),"{0:.2f}".format(total+total2)])
        data.append(['Descuento',"{0:.2f}".format(descuento),"{0:.2f}".format(descuento2),"{0:.2f}".format(descuento+descuento2)])
        data.append(['Impuestos',"{0:.2f}".format(iva),"{0:.2f}".format(iva2),"{0:.2f}".format(iva+iva2)])
        data.append(['Total',"{0:.2f}".format(total-descuento+iva),"{0:.2f}".format(total2-descuento2+iva2),"{0:.2f}".format((total-descuento+iva)+(total2-descuento2+iva2))])
        return data
    



    def getPagosAll(self):
        fecha=self.name
        ayer=datetime(fecha.year, fecha.month, fecha.day)
        prime_day_of_month=datetime(fecha.year, fecha.month, 1)
        last_date_of_month = datetime(fecha.year, fecha.month, 1) + relativedelta(months=1, days=-1)
        hoy_temp=fecha+relativedelta(days=1)
        hoy=datetime(hoy_temp.year, hoy_temp.month, hoy_temp.day)
        lines=self.env['account.payment'].search([['payment_date','>=',prime_day_of_month],['payment_date','<',ayer]])
        lines2=self.env['account.payment'].search([['payment_date','=',fecha]])
        lines=lines.filtered(lambda x:x.payment_type!='outbound')
        lines2=lines2.filtered(lambda x:x.payment_type!='outbound')
        j=self.env['account.journal'].search([['type','not in',['purchase','general']]])
        data=[]
        for jo in j:
            ayer=sum(lines.filtered(lambda x:x.journal_id.id==jo.id).mapped('monto_moneda'))
            hoy=sum(lines2.filtered(lambda x:x.journal_id.id==jo.id).mapped('monto_moneda'))
            data.append([jo.name,"{0:.2f}".format(ayer),"{0:.2f}".format(hoy),"{0:.2f}".format(hoy+ayer)])
        return data

    def getFacturasSinPago(self):
        inmediato=self.env.ref('account.account_payment_term_immediate')
        facturas=self.env['account.move'].search([['invoice_payment_term_id','=',inmediato.id],['amount_residual_signed','!=',0],['state','=','posted'],['type','=','out_invoice']])
        data=[]
        for f in facturas:
            data.append([f.name,f.partner_id.name,f.invoice_date,"{0:.2f}".format(f.amount_residual_signed)])
        return data

class CierreConf(models.Model):
    _name = "cierre.conf"

    user_id = fields.Many2one('res.users', 'Usuario', required=1)
    journal_ids = fields.Many2many('account.journal', string='Diarios')
    monto_inicio = fields.Float('Monto Inicio caja')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    

