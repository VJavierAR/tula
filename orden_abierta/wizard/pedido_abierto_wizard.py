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
        comodel_name="pedido.abierto.linea",
        string="Lineas de pedido abierto",
        domain="[('es_de_sale_order', '=', False)]"
    )

    def crear_orden(self):
        _logger.info("generando orden")
        pedido_abierto = self.env['pedido.abierto'].search([('id', '=', self.pedido_abierto_id)])

        for linea in self.lineas_pedidos:
            cantidad_sobrante = linea.cantidad_restante - linea.product_uom_qty
            if cantidad_sobrante < 0:
                mensajeTitulo = "Alerta"
                display_msg = "La cantidad de pedida no puede exceder de la cantidad restante."
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
            if linea.linea_confirmada:
                mensajeTitulo = "Alerta"
                display_msg = "Una de las lineas no tiene cantidades restantes por entregar."
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

        sale_directa = self.env['sale.order'].create({
            'partner_id': pedido_abierto.partner_id.id,
            'payment_term_id': pedido_abierto.plazo_de_pago.id,
            # 'company_id': self.order_line_ids[0].order_id.company_id.id,
            # 'picking_policy': self.order_line_ids[0].order_id.picking_policy,
        })
        sale_directa.write({
            'pedido_abierto_origen': self.pedido_abierto_id
        })
        id_sale_directa = sale_directa.id

        for linea in self.lineas_pedidos:
            linea.cantidad_restante = linea.cantidad_restante - linea.product_uom_qty
            linea.cantidad_entregada = linea.cantidad_entregada + linea.product_uom_qty

            linea_sale_order_line = self.env['sale.order.line'].create({
                'partner_id': linea.partner_id.id,
                'order_id': id_sale_directa,
                'linea_abierta_rel': linea.id,
                'codigo_cliente': linea.codigo_cliente,
                'pedido_cliente': linea.pedido_cliente,
                'fecha_programada': linea.fecha_programada,
                'codigo_alterno': linea.codigo_alterno,
                'cantidad_reservada': linea.cantidad_reservada,
                'creado_desde_pedido_abierto': linea.creado_desde_pedido_abierto,
                'cantidad_original': linea.cantidad_original,
                'cantidad_facturada': linea.cantidad_facturada,
                'cantidad_entregada': linea.cantidad_entregada,
                'cantidad_restante': linea.cantidad_restante,
                'es_de_sale_order': True,
            })

            #linea_duplicada = linea.dup_line_to_order(order_id=id_sale_directa)
            # linea_duplicada.pedido_abierto_rel = False
            #v linea_duplicada.es_de_sale_order = True

            linea.write({
                'linea_relacionada': [(4, linea_sale_order_line.id, 0)]
            })

            if linea.cantidad_restante == 0:
                linea.linea_confirmada = True

        todas_validadas = True
        for linea in pedido_abierto.lineas_pedido:
            # linea.order_id = id_sale_directa
            # linea.linea_confirmada = True
            if not linea.linea_confirmada:
                todas_validadas = False

        if todas_validadas:
            pedido_abierto.write({
                'state': 'confirmado'
            })

        sale_directa.action_confirm()
        display_msg = "Se genero orden directa de un pedido abierto: <br/>Pedido abierto: " + pedido_abierto.name
        sale_directa.message_post(body=display_msg)

        display_msg = "Se genero orden directa de un pedido abierto: <br/>Orden directa: " + sale_directa.name
        pedido_abierto.message_post(body=display_msg)

        mensajeTitulo = "Alerta"
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
