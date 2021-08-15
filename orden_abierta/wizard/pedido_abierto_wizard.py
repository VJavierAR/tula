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
    lineas_pedidos = fields.Many2many(
        comodel_name="sale.order.line",
        string="Lineas de pedido abierto"
    )

    def crear_orden(self):
        _logger.info("generando orden")
        pedido_abierto = self.env['pedido.abierto'].search([('id', '=', self.pedido_abierto_id)])
        sale_directa = self.env['sale.order'].create({
            'partner_id': pedido_abierto.partner_id.id,
            # 'company_id': self.order_line_ids[0].order_id.company_id.id,
            # 'picking_policy': self.order_line_ids[0].order_id.picking_policy,
            # 'payment_term_id': self.payment_term_id.id
        })
        sale_directa.write({
            'pedido_abierto_origen': self.pedido_abierto_id
        })
        id_sale_directa = sale_directa.id

        for linea in pedido_abierto.lineas_pedido:
            linea.order_id = id_sale_directa

        pedido_abierto.write({
            'state': 'confirmado'
        })
