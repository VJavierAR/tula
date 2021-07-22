from odoo import models
import base64
from odoo import api, fields, models, _, SUPERUSER_ID
import hashlib 


class ResUser(models.Model):
    _inherit = "res.users"
    max_discount=fields.Integer('Descuento maximo')
