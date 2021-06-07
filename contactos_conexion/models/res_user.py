from odoo import models, fields, api,_
import logging, ast

_logger = logging.getLogger(__name__)


class Users(models.Model):
    _inherit = 'res.users'

    codigo_vendedor = fields.Char(
        string="Código de vendedor",
        store=True
    )
    meta_facturacion = fields.Float(
        string="Meta de facturación",
        store=True,
        default=0
    )

