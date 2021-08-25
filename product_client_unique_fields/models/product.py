# -*- coding: utf-8 -*-
from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.template"

    _sql_constraints = [
            ('default_code_uniq', 'unique(default_code)', "La referencia interna ya fue asignada a otro producto"),
        ]
