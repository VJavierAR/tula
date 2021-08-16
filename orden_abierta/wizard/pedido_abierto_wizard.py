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
            linea.linea_confirmada = True

        pedido_abierto.write({
            'state': 'confirmado'
        })
        sale_directa.action_confirm()
        display_msg = "Se genero orden directa de un pedido abierto: <br/>Pedido abierto: " + pedido_abierto.name
        sale_directa.message_post(body=display_msg)

        display_msg = "Se genero orden directa de un pedido abierto: <br/>Orden directa: " + sale_directa.name
        pedido_abierto.message_post(body=display_msg)

        wiz = self.env['sale.order.alerta'].create({'mensaje': display_msg})
        view = self.env.ref('orden_abierta.sale_order_alerta_view')
        return {
            'name': _(mensajeTitulo),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order.alerta',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }
