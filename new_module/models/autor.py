# -*- coding: utf-8 -*-

from odoo import models, fields, api


class autor(models.Model):
    _name = 'new_module.autor'
    _description = 'new_module.autor'
    
    
    nombre = fields.Char()
    apellido_paterno = fields.Char()
    apellido_materno = fields.Char()    