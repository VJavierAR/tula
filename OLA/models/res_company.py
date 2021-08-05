from odoo import models, fields, api,_
import logging, ast

_logger = logging.getLogger(__name__)

class partner(models.Model):
    _inherit = 'res.company'
    auto_picking=fields.Boolean()

    limite_credito_global = fields.Monetary(
        string = "Límite de crédito global"
    )