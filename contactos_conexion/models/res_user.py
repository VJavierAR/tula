from odoo import models, fields, api,_
import logging, ast

_logger = logging.getLogger(__name__)


class Users(models.Model):
    _inherit = 'res.users'

    codigo_vendedor = fields.Char(
        string="Código de vendedor",
        store=True
    )

    @api.model
    def get_meta_facturacion(self):
        # for rec in self:
        totales = self.env['sale.order'].search(
            [
                ('user_id', '=', self.id),
                ('state', '=', 'sale')
            ]
        ).mapped('amount_total')
        _logger.info("id: " + str(self.id))
        _logger.info("totales: " + str(totales))
        suma_totales = 0
        for total in totales:
            suma_totales += total
        # rec.meta_faturacion = suma_totales
        return suma_totales

    meta_facturacion = fields.Float(
        string="Meta de facturación",
        store=True,
        # default=0
        default=lambda self: self.get_meta_facturacion()
        # compute='_compute_meta_facturacion'
    )

    # @api.depends()
    def _compute_meta_facturacion(self):
        _logger.info("entreeeeeeeeeeeeeeeeeeeeeee: ")
        for rec in self:
            totales = self.env['sale.order'].search(
                [
                    ('user_id', '=', rec._origin.id),
                    ('state', '=', 'sale')
                ]
            ).mapped('amount_total')
            _logger.info("id: " + str(rec._origin.id))
            _logger.info("totales: " + str(totales))
            suma_totales = 0
            for total in totales:
                suma_totales += total
            rec.meta_facturacion = suma_totales



