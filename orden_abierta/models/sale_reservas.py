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


class SaleOrderReservas(models.Model):
    _name = 'sale.order.reservas'
    _description = 'Reservas realizadas'

    sale_id = fields.Many2one(
        comodel_name='sale.order',
        string='Pedido de venta relacionado'
    )
    pedido_venta = fields.Text(
        string="Pedido de venta de línea"
    )
    cantidad_reservada = fields.Float(
        string="Cantidad reservada",
        default=0
    )
