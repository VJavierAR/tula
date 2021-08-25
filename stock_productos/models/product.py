# -*- coding: utf-8 -*-

from odoo import models, fields, api
from email.utils import formataddr
from odoo.exceptions import UserError, RedirectWarning
from odoo import exceptions, _
import logging, ast
import datetime, time
import pytz
import base64
import requests
import json

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    stock_bodegas = fields.Text(
        string='Stock en bodegas',
        compute="_compute_obten_stock_bodegas"
    )

    def _compute_obten_stock_bodegas(self):
        for rec in self:
            info = ""
            stock = rec.sudo().product_variant_id.stock_quant_ids.filtered(
                lambda x:
                    x.company_id.id is not False and
                    x.quantity >= 0 and
                    x.location_id.usage == 'internal' and
                    x.location_id.mostrar_stock is True
            )
            for data in stock:
                info += str(data.location_id.display_name) + ": " + str(data.quantity) + "\n"
            rec['stock_bodegas'] = info
