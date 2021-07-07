from odoo import models, fields, api,_
import logging, ast

_logger = logging.getLogger(__name__)


class Users(models.Model):
    _inherit = 'res.users'

    codigo_vendedor = fields.Char(
        string="Código de vendedor",
        store=True
    )
    meta_facturacion = fields.Float(
        string="Meta de facturación",
        store=True,
        # default=0
        default=lambda self: self.get_meta_facturacion()
    )

    @api.model
    def get_meta_facturacion(self):
        totales = self.env['sale.order'].search(
            [
                ('user_id', '=', self.id),
                ('state', '=', 'sale')
            ]
        ).mapped('amount_total')
        suma_totales = 0
        for total in totales:
            suma_totales += total

        return suma_totales
