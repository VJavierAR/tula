# -*- coding: utf-8 -*-

from odoo import models, fields, api
from email.utils import formataddr
from odoo.exceptions import UserError, RedirectWarning
from odoo import exceptions, _
import logging, ast
import datetime, time
import pytz
import base64
import requests
import json

_logger = logging.getLogger(__name__)


class SaleOrderLineOrdenAbierta(models.Model):
    _inherit = 'sale.order.line'
    _description = 'línea de pedido orden abierta'

    codigo_cliente = fields.Text(
        string="Código cliente",
        copy=True
    )
    pedido_cliente = fields.Text(
        string="Pedido cliente",
        copy=True
    )
    fecha_programada = fields.Date(
        string="Programación"
    )
    codigo_alterno = fields.Text(
        string="Código alterno",
        copy=True
    )
    cantidad_reservada = fields.Text(
        string="Cantidad reservada",
        copy=True
    )
    default_code_product = fields.Char(
        string="Referencia interna",
        related="product_id.default_code"
    )
    confirma_venta_directa = fields.Boolean(
        string="Confirma venta directa",
        default=False
    )
    linea_confirmada = fields.Boolean(
        string="Línea confirmada",
        default=False
    )
    pedido_abierto_rel = fields.Many2one(
        comodel_name="pedido.abierto",
        string="Pedido abierto rel",
        required=False,
        store=True,
        index=True,
    )
    order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Order Reference',
        required=False,
        ondelete='cascade',
        index=True,
        copy=False
    )

    @api.onchange('product_id', 'product_uom_qty')
    def cambia_producto(self):
        if self.product_id.id:
            # Obtiene código de cliente
            for codigo in self.product_id.codigos_de_producto:
                if self.order_partner_id.id == codigo.cliente.id:
                    self.codigo_cliente = codigo.codigo_producto


            # Cantidad reservada
            estados_no_aprobados = ['draft', 'sent']
            ordenes = self.env['sale.order'].search(
                [
                    ('state', 'in', estados_no_aprobados),
                    ('es_orden_abierta', '=', True)
                ])
            cantidad_dispobible = self.product_id.qty_available
            cantidad_reservada_suma = 0
            for orden in ordenes:
                for linea in orden.order_line:
                    if linea.product_id.id == self.product_id.id:
                        cantidad_reservada_suma += linea.product_uom_qty

            if cantidad_reservada_suma > 0:
                self.cantidad_reservada = cantidad_dispobible - cantidad_reservada_suma
            else:
                self.cantidad_reservada = 0


            # Mensaje inventario actual
            cantidad_a_vender = self.product_uom_qty
            cantidad_prevista = self.product_id.virtual_available
            cantidad_entrada = self.product_id.incoming_qty
            cantidad_pedidos_abiertos = cantidad_reservada_suma
            cantidad_disponible_menos_cantidad_pa = cantidad_dispobible - cantidad_pedidos_abiertos
            _logger.info("cantidad_a_vender: " + str(cantidad_a_vender) + " > cantidad_disponible_menos_cantidad_pa:" + str(cantidad_disponible_menos_cantidad_pa))
            if cantidad_a_vender > cantidad_disponible_menos_cantidad_pa:

                nombre_producto = self.product_id.name
                almacenes_stock = self.product_id.stock_quant_ids.filtered(
                    lambda x:
                    x.company_id.id is not False and
                    x.quantity >= 0 and
                    x.location_id.usage == 'internal'
                )
                nombre_almacen = ""
                for data in almacenes_stock:
                    nombre_almacen += str(data.location_id.display_name) + ": " + str(data.quantity) + "\n"
                mensaje = "Planea vender " + str(
                    cantidad_a_vender) + " de " + nombre_producto + " pero solo tiene " + str(cantidad_dispobible)
                mensaje += " en los siguientes almacenes:\nAlmacén: cantidad\n" + nombre_almacen + "\n"
                mensaje += "Existen " + str(cantidad_disponible_menos_cantidad_pa)
                mensaje += " disponibles (Cantidad a mano, menos la cantidad de pedidos abiertos).\n\n"
                mensaje += "Cantidad requerida: " + str(cantidad_a_vender) + "\n"
                mensaje += "Cantidad a mano: " + str(cantidad_dispobible) + "\n"
                mensaje += "Cantidad a prevista: " + str(cantidad_prevista) + "\n"
                mensaje += "Total cantidad en tránsito: " + str(cantidad_entrada) + "\n"
                return {
                    'warning': {
                        'title': _('Inventario actual!'),
                        'message': _(mensaje),
                    },
                }

    # @api.multi
    def dup_line_to_order(self, order_id=None):
        return self.copy(default={'order_id': order_id})
