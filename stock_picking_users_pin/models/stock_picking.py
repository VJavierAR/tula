# -*- coding: utf-8 -*-
from odoo import models, fields


class StockPicking(models.Model):
    _inherit = "stock.picking"

    state = fields.Selection(selection_add=[('printed', 'Impreso')])
    user_print_id = fields.Many2one(comodel_name="res.users", string="Usuario que imprimió", tracking=True, copy=False, required=False)
    user_validate_id = fields.Many2one(comodel_name="res.users", string="Usuario que validó", tracking=True, copy=False, required=False)
