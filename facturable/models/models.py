#-*- coding: utf-8 -*-

from odoo import models, fields, api


class facturable(models.Model):
    _inherit = 'sale.order.line'
    facturable=fields.Float('Facturable')

class facturable(models.Model):
    _inherit = 'stock.picking'
    
    #def write(self, values):
    #	if('state' in values):
