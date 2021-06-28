# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta
import pytz
import logging, ast

_logger = logging.getLogger(__name__)


class Reparaciones(models.Model):
    _inherit = 'sale.order'
    _description = 'reparaciones.reparaciones'

    flota = fields.Many2one(
        comodel_name='fleet.vehicle',
        string='Vehículo'
    )

    responsable = fields.Many2one(
        comodel_name='res.users',
        string='Responsable'
    )

    servicios = fields.One2many(
        comodel_name='sale.order.line',
        inverse_name='reparaciones_rel',
        string='Servicios'
    )
