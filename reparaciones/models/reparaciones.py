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

    @api.onchange('state')
    def conf(self):
        if self.state == 'sale' and self.picking_ids:
            for linea in self.order_line:
                if linea.tipo == 'remove':
                    for picking in self.picking_ids:
                        if picking.move_line_ids_without_package:
                            for linea_orden in picking.move_line_ids_without_package:
                                if linea_orden.product_id.id == linea.product_id.id:
                                    self.picking_ids.move_line_ids_without_package = (3, linea_orden.id, 0)

