# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta
import pytz
import logging, ast

_logger = logging.getLogger(__name__)


class SOL(models.Model):
    _inherit = 'sale.order.line'
    _description = 'reparaciones.sale.order.line'

    tipo = fields.Selection(
        selection=[('add', 'Añadir'),('remove','Eliminar')],
        string='Tipo'
    )


