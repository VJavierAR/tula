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


class Partner(models.Model):
    _inherit = 'res.partner'

    referencia_interna = fields.Text(
        string="Referencia interna"
    )
    horario_de_entrega = fields.Datetime(
        string="Horario de entrega"
    )
