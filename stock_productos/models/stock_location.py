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
    _inherit = 'stock.location'

    mostrar_stock = fields.Boolean(
        string="Consiltar Stock",
        default=False,
        company_dependent=True
    )
