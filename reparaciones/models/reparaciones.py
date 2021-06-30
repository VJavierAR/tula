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

    @api.depends('state')
    def conf(self):
        for rec in self:
            _logger.info("conf()****************")
            if rec.state == 'sale' and rec.picking_ids:
                _logger.info("entrando si el estado es sale y tiene picking_ids")
                for linea in rec.order_line:
                    if linea.tipo == 'remove':
                        for picking in rec.picking_ids:
                            if picking.move_line_ids_without_package:
                                for linea_orden in picking.move_line_ids_without_package:
                                    if linea_orden.product_id.id == linea.product_id.id:
                                        picking.move_line_ids_without_package = (3, linea_orden.id, 0)

