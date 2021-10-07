# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class requirement_and_proposal(models.Model):
#     _name = 'requirement_and_proposal.requirement_and_proposal'
#     _description = 'requirement_and_proposal.requirement_and_proposal'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
