from odoo import models, fields, api,_
import logging, ast

_logger = logging.getLogger(__name__)


class Users(models.Model):
    _inherit = 'crm.team'

    invoiced_target = fields.Float(
        string="Meta de facturación",
        store=False,
        compute='_compute_meta_facturacion'
    )

    def _compute_meta_facturacion(self):
        for rec in self:
            totales = self.env['sale.order'].search(
                [
                    ('team_id', '=', rec._origin.id),
                    ('state', '=', 'sale')
                ]
            ).mapped('amount_total')
            suma_totales = 0
            for total in totales:
                suma_totales += total
            rec.invoiced_target = suma_totales