# -*- coding: utf-8 -*-
from odoo import models


class ResUsers(models.Model):
    _inherit = "sale.order"

    def button_priority(self):
        for p in self.picking_ids:
            p.priority = '3'