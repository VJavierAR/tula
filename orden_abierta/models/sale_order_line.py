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

    @api.onchange('product_id')
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

    # @api.multi
    def dup_line_to_order(self, order_id=None):
        return self.copy(default={'order_id': order_id})
