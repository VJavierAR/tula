# -*- coding: utf-8 -*-
from odoo import models, fields


class ResUsers(models.Model):
    _inherit = "res.users"

    user_pin = fields.Char(string='Pin de acceso', required=False)
    _sql_constraints = [('user_pin_uniq', 'unique (user_pin)', "El pin ya está asignado a otro usuario.")]
