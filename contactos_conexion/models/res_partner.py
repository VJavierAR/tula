from odoo import models, fields, api,_
import logging, ast

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = 'res.partner'

    codigo_naf = fields.Char(
        string="Código Naf",
        store=True
    )
    tipo = fields.Char(
        string="Tipo",
        store=True
    )
    cedula = fields.Char(
        string="Cedula",
        store=True
    )
