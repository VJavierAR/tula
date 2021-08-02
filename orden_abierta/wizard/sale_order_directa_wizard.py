# -*- coding: utf-8 -*-
from odoo import fields, models, api,_
from odoo.exceptions import UserError
from odoo import exceptions
import logging, ast
_logger = logging.getLogger(__name__)


class OrdenAbiertaToDirecta(models.TransientModel):
    _name = 'orden.abierta.to.directa'
    _description = 'Genera orden directa con base a ordenes abiertas'

    def _default_order_line_ids(self):
        return self.env['sale.order.line'].browse(
            self.env.context.get('active_ids'))

    order_line_ids = fields.Many2many(
        string='Ordenes',
        comodel_name="sale.order.line",
        default=lambda self: self._default_order_line_ids(),
        help="",
    )

    def generar_orden(self):
        for linea in self.order_line_ids:
            _logger.info("line: " + str(linea))


class Alerta(models.TransientModel):
    _name = 'sale.order.alerta'
    _description = 'Alerta'

    mensaje = fields.Text(
        string='Mensaje'
    )
