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
        readonly=False,
        domain="[('es_de_sale_order', '=', False)]"
    )

    def generar_orden(self):
        _logger.info("generando orden")

        mensajeTitulo = "Alerta"
        cliente_id = self.order_line_ids[0].order_partner_id.id
        _logger.info("cliente_id: " + str(cliente_id))
        for linea in self.order_line_ids:
            if linea.order_partner_id.id != cliente_id:
                display_msg = "Una línea de pedido tiene diferente cliente"
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
            'partner_id': cliente_id,
            # 'company_id': self.order_line_ids[0].order_id.company_id.id,
            # 'picking_policy': self.order_line_ids[0].order_id.picking_policy,
        })
        # sale_directa.write({
        #   'pedido_abierto_origen': self.pedido_abierto_id
        # })
        id_sale_directa = sale_directa.id

        name_pedidos_abiertos = []
        ids_pedidos_abiertos = []
        for linea in self.order_line_ids:
            # linea.order_id = id_sale_directa
            # linea.linea_confirmada = True
            linea.cantidad_restante = linea.cantidad_restante - linea.product_uom_qty
            linea.cantidad_entregada = linea.cantidad_entregada + linea.product_uom_qty

            linea_duplicada = linea.dup_line_to_order(order_id=id_sale_directa)
            # linea_duplicada.pedido_abierto_rel = False
            linea_duplicada.es_de_sale_order = True
            linea_duplicada.linea_relacionada = linea_duplicada.id

            if linea.cantidad_restante == 0:
                linea.linea_confirmada = True

            ids_pedidos_abiertos.append(linea.pedido_abierto_rel.id)
            name_pedidos_abiertos.append(linea.pedido_abierto_rel.name)

        for id_pedido_abierto in ids_pedidos_abiertos:
            lineas_de_pedido_abierto_sin_confirmar = self.env['sale.order.line'].search([
                ('pedido_abierto_rel', '=', id_pedido_abierto),
                ('linea_confirmada', '=', False),
                ('creado_desde_pedido_abierto', '=', True)
            ]).mapped('id')

            if len(lineas_de_pedido_abierto_sin_confirmar) == 0:
                pedido_abierto = self.env['pedido.abierto'].search([('id', '=', id_pedido_abierto)])
                pedido_abierto.write({
                    'state': 'confirmado'
                })

        sale_directa.action_confirm()
        display_msg = "Se genero orden directa de uno o más pedidos abiertos: <br/>Pedido(s) abierto(s): " + str(name_pedidos_abiertos)
        sale_directa.message_post(body=display_msg)

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

        """
        mensajeTitulo = "Alerta"
        cliente_id = self.order_line_ids[0].order_partner_id.id
        for line in self.order_line_ids:
            if line.order_partner_id.id != cliente_id:
                display_msg = "Una línea de pedido tiene diferente cliente"
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
            'partner_id': cliente_id,
            'company_id': self.order_line_ids[0].order_id.company_id.id,
            'picking_policy': self.order_line_ids[0].order_id.picking_policy,
            # 'payment_term_id': self.payment_term_id.id
        })
        id_sale_directa = sale_directa.id
        for line in self.order_line_ids:
            if not line.linea_confirmada:
                linea_generada = line.dup_line_to_order(order_id=id_sale_directa)
                line.linea_confirmada = True
                linea_generada.linea_confirmada = True

        if len(sale_directa.order_line) == 0:
            sale_directa.unlink()
            display_msg = "No se genero orden directa al no tener lineas que confirmar"
            # self.message_post(body=display_msg)
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
        else:
            display_msg = "Se genero orden directa con las líneas seleccionadas: <br/>Orden generada: " + sale_directa.name
            # self.message_post(body=display_msg)
            sale_directa.action_confirm()
            for linea in self.order_line_ids:
                linea.order_id.message_post(body=display_msg)
                confirmadas = linea.order_id.mapped('order_line.linea_confirmada')
                if False not in confirmadas:
                    linea.order_id.state = 'sale'

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
        """


class Alerta(models.TransientModel):
    _name = 'sale.order.alerta'
    _description = 'Alerta'

    mensaje = fields.Text(
        string='Mensaje'
    )
