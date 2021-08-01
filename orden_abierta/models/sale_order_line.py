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
        string="Código cliente"
    )
    fecha_programada = fields.Date(
        string="Programación",
    )
    codigo_alterno = fields.Text(
        string="Código alterno"
    )

    @api.onchange('product_id')
    def cambia_producto(self):
        if self.product_id.id:
            for codigo in self.product_id.codigos_de_producto:
                if self.order_partner_id.id == codigo.cliente.id:
                    self.codigo_cliente = codigo.codigo_producto
