# -*- coding: utf-8 -*-

from odoo import models, fields, api


class compras(models.Model):
    _inherit = 'account.move'
    tipo=fields.Selection([('1','Combustible'), ('2','Compras'), ('3','Pequeño Cont.'), ('4','Servicios'), ('5','Import')],'Tipo')

