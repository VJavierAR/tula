# -*- coding: utf-8 -*-
from odoo import fields, models, api,_
from odoo.exceptions import UserError
from odoo import exceptions
from odoo.exceptions import AccessDenied
import logging, ast
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit='account.move'

    cambio_no_permitido = fields.Text(
        string='Intento de cambio no permitido',
        compute='_compute_cambio_no_permitido'
    )

    @api.onchange('invoice_payment_term_id', 'amount_total')
    def cambio_no_permitido(self):
        termino_antes = self._origin.invoice_payment_term_id.name
        termino_despues = self.invoice_payment_term_id.name

        _logger.info("termino_antes: " + str(termino_antes) + " termino_despues: " + str(termino_despues))

        id_usuario_login = self._uid.id

        usuarios_con_permisos = self.env['res.groups'].sudo().search(
            [
                ("name", "=", "Confirma pedido de venta que excede límite de crédito")
            ]
        ).mapped('users').mapped('id')
        _logger.info("usuarios_con_permisos: " + str(usuarios_con_permisos))
        if not id_usuario_login in usuarios_con_permisos:
            raise AccessDenied(_("No tiene los permisos para realizar el cambio de \"terminos de pago\" o \"costos de productos\"."))