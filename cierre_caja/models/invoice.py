from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime

medio_pago_values = [('cheque', 'Cheque'), ('efectivo', 'Efectivo'), ('datafono', 'Datafono Local'), ('transferencia', 'Transferencia')]

class AccountPayment(models.Model):
    _inherit = "account.payment"

    cierre_id = fields.Many2one('cierre.caja')
    incluir = fields.Boolean('Incluir', default=False)
    medio_pago = fields.Selection(medio_pago_values, string='Medio Pago')

class CierreLineas(models.Model):
    _name = "cierre.caja.lineas"

    name = fields.Many2one('account.journal', 'Diario')
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
            line.monto_calculado = sum(pagos.filtered(lambda p: p.journal_id == line.name).mapped('amount'))
            line.diferencia = line.monto_calculado - line.monto_reportado

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
            cierre.update(dict(monto_cierre_calculado = total_pagos , monto_cierre=monto_reportado))

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
    
    def compute_monto_cierre_acumulado(self):
        fecha=fields.Datetime.now()
        prime_day_of_month=datetime.datetime(fecha.year, fecha.month, 1)
        last_date_of_month = datetime.datetime(fecha.year, fecha.month, 1) + relativedelta(months=1, days=-1)
        data=self.search([['name','>=',prime_day_of_month],['name','<=',last_date_of_month]])
        self.monto_cierre_acumulado=sum(data.mapped('diferencia'))
    def print_report(self):
        return self.env.ref('cierre_caja.cierre_caja_report').report_action(self)

    def set_progress(self):
        jounal_env = self.env['account.journal']
        for cierre in self:
            vals = dict(state='progress')
            journal_ids = jounal_env.search([('type', 'in', ('bank', 'cash'))])
            vals['desglose_pagos'] = []
            vals['desglose_pagos2'] = []
            for j in journal_ids:
                vals['desglose_pagos'].append((0, 0, {'name': j.id, 'cierre_id': cierre.id}))
            for m in medio_pago_values:
                vals['desglose_pagos2'].append((0, 0, {'name': m[1], 'internal_name': m[0], 'cierre_id': cierre.id}))
            cierre.write(vals)

    def set_closed(self):
        fecha=fields.Datetime.now()
        last_date_of_month = datetime.datetime(fecha.year, fecha.month, 1) + relativedelta(months=1, days=-1)
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
                [('create_date', '>=', cierre.name), ('create_date', '<=', cierre_dia), ('create_uid', '=', cierre.user_id.id), ('state', 'not in', ('draft', 'cancelled')), ('partner_type', '=', 'customer'), ('payment_type', 'in', ('inbound', 'outbound'))])
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


class CierreConf(models.Model):
    _name = "cierre.conf"

    user_id = fields.Many2one('res.users', 'Usuario', required=1)
    journal_ids = fields.Many2many('account.journal', string='Diarios')
    monto_inicio = fields.Float('Monto Inicio caja')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    

