# -*- coding: utf-8 -*-

from odoo import models, fields, api


class compras(models.Model):
    _inherit = 'purchase.order'
    tipo=fields.Selection(string='Tipo',[('1','Combustible'), ('2','Compras'), ('3','Pequeño Cont.'), ('4','Servicios'), ('5','Import')])

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
