#-*- coding: utf-8 -*-

from odoo import models, fields, api


class facturable(models.Model):
    _inherit = 'sale.order.line'
    facturable=fields.Double('Facturable')
    

