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
        inverse_name='order_id',
        string='Servicios',

    )
    check=fields.Boolean(default=False)

    operations = fields.One2many(
        'repair.product', 'repair_id', 'Parts',
        copy=True, readonly=True, states={'draft': [('readonly', False)]})
    fees_lines = fields.One2many(
        'repair.service', 'repair_id', 'Operations',
        copy=True, readonly=True, states={'draft': [('readonly', False)]})




    # @api.depends('state')
    def conf(self):
        self.action_confirm()
        _logger.info("conf()****************")
        if self.state == 'sale':
            for pi in self.picking_ids.filtered(lambda x:x.state not in ['done','cancel']):
                pi.do_unreserve()
            for linea in self.order_line.filtered(lambda x:x.tipo=='remove'):
                p=self.env['stock.move'].search([['sale_line_id','=',linea.id],['state','not in',['done','cancel','assigned']]])
                p._action_cancel()
                p.unlink()
            for pi in self.picking_ids.filtered(lambda x:x.state not in ['done','cancel']):
                pi.action_assign()
                #if linea.tipo == 'remove':
                    #for picking in self.picking_ids:
                    #    if picking.move_line_ids_without_package:
                    #       for linea_orden in picking.move_line_ids_without_package:
                    #            if linea_orden.product_id.id == linea.product_id.id:
                    #                picking.move_line_ids_without_package = (3, linea_orden.id, 0)

    def validate_picking(self):
        if self.state == 'sale':
            P=self.picking_ids.filtered(lambda x:x.state not in ['done','cancel'])
            for pi in P:
                if pi.state == 'assigned':
                    pi.action_confirm()
                    pi.move_lines._action_assign()
                    pi.action_assign()
                    return pi.button_validate()
