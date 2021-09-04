# -*- coding: utf-8 -*-

from odoo import models, fields, api
#comentario de control

class books(models.Model):
    _name = 'new_module.books'
    _description = 'new_module.books'
    
    autors_ids = fields.Many2many(
       'new_module.autor',
        string = 'Autores'
    )
    titulo = fields.Char()
    