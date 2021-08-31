from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import logging, ast
_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = "account.payment"
    bandera=fields.Boolean(default=False)

    # @api.onchange('journal_id')
    # def checkPago(self):
    #     conf_usuario = self.env["cierre.conf"].search([('user_id', '=', self.env.user.id)], limit=1)
    #     for record in self:
    #         _logger.info(record.journal_id.id)
    #         if(record.journal_id.id!=False):
    #             if record.journal_id.id not in conf_usuario.journal_ids.ids:
    #                 raise UserError('Usted no puede registrar pagos en este diario.')

    def validar_caja(self, journal_id, conf_usuario):
        cierre_env = self.env['cierre.caja']
        journal_env = self.env['account.journal']
        if journal_id not in conf_usuario.journal_ids.ids:
            raise UserError('Usted no puede registrar pagos en este diario.')
        if journal_env.search([('id', '=', journal_id)]).type in ('cash', 'bank'):
            cierre_obj = cierre_env.search([('create_uid', '=', self.env.user.id), ('state', '=', 'progress')],
                                           limit=1)
            if not cierre_obj:
                raise UserError('Usted no puede registrar pagos si no tiene activo un cierre de caja.')
            elif (cierre_obj.name - timedelta(hours=6)).date() != (datetime.now() - timedelta(hours=6)).date():
                raise UserError('La caja abierta no es de hoy, debe primero cerrar la caja abierta y luego abrir una nueva.')


    @api.model_create_multi
    def create(self, vals_list):
        conf_usuario = self.env["cierre.conf"].search([('user_id', '=', self.env.user.id)], limit=1)
        if conf_usuario:
            for vl in vals_list:
                if vl['payment_type'] in ('inbound', 'outbound') and vl['partner_type'] == 'customer':
                    self.validar_caja(vl['journal_id'], conf_usuario)
        return super(AccountPayment, self).create(vals_list)

    def write(self, vals):
        conf_usuario = self.env["cierre.conf"].search([('user_id', '=', self.env.user.id)], limit=1)
        #payment_type = vals.get('payment_type', self[0].payment_type)
        payment_type=vals['payment_type'] if('payment_type' in vals) else self.payment_type
        partner_type=vals['partner_type'] if('partner_type' in vals) else self.partner_type
        bandera=vals['bandera'] if('bandera' in vals) else False
        if conf_usuario and payment_type != 'transfer' and bandera==True:
            if 'journal_id' in vals:
                if payment_type in ('inbound', 'outbound') and partner_type == 'customer':
                    self.validar_caja(vals['journal_id'], conf_usuario)
            else:
                if payment_type in ('inbound', 'outbound') and partner_type == 'customer':
                    self.validar_caja(self.journal_id.id, conf_usuario)
        return super(AccountPayment, self).write(vals)


class Diarios(models.Model):
    _inherit='account.journal'
    quitar_diario=fields.Boolean()
class TypePago(models.Model):
    _name='tipo.pago'
    _description='Agregación de tipo de pago'
    name=fields.Char()