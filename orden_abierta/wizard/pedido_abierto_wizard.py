# -*- coding: utf-8 -*-
from odoo import fields, models, api,_
from odoo.exceptions import UserError
from odoo import exceptions
import logging, ast
_logger = logging.getLogger(__name__)


class PedidoAbiertoWizard(models.TransientModel):
    _name = 'pedido.abierto.wizard'
    _description = 'Genera pedido con base a lineas de pedido abierto'

    pedido_abierto_id = fields.Integer(
        string="id pedido abierto"
    )
    lineas_pedidos = fields.One2many(
        comodel_name="sale.order.line",
        inverse_name="pedido_abierto_rel",
        string="Lineas de pedido abierto"
    )

    def crear_orden(self):
        _logger.info("generando orden")