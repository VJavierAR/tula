# -*- coding: utf-8 -*-
from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    _sql_constraints = [
            ('vat_uniq', 'unique(vat)', "El NIF ya fue asignado a otro cliente"),
        ]
