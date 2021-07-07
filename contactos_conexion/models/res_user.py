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
        store=False,
        compute='_compute_meta_facturacion'
    )

    def _compute_meta_facturacion(self):
        for rec in self:
            totales = self.env['sale.order'].search(
                [
                    ('user_id', '=', rec._origin.id),
                    ('state', '=', 'sale')
                ]
            ).mapped('amount_total')
            suma_totales = 0
            for total in totales:
                suma_totales += total
            rec.meta_facturacion = suma_totales
