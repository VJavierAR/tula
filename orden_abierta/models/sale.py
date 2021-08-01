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


class SaleOrderOrdenAbierta(models.Model):
    _inherit = 'sale.order'
    _description = 'Orden abierta'

    es_orden_abierta = fields.Boolean(
        string="¿Es odern abierta?"
    )

    def conf(self):
        orden_abierta = False
        for line in self.order_line:
            if line.fecha_programada:
                orden_abierta = True
                break
        if orden_abierta:
            self.es_orden_abierta = True
        else:
            self.action_confirm()

    @api.onchange('order_line')
    def cambian_lineas(self):
        if self.order_line:
            for linea in self.order_line:
                if linea.fecha_programada:
                    self.es_orden_abierta = True
                    break
