from odoo import models, fields, api,_
import logging, ast

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = 'res.partner'

    historal_fac_tramitadas = fields.One2many(
        comodel_name="facturas.tramites",
        inverse_name="clientes",
    )