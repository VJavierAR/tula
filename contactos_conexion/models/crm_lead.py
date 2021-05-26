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
_logger = logging.getLogger(__name__)


class CRM(models.Model):
    _inherit = 'crm.lead'
    _description = 'Cambios'

    lugar_trabajo = fields.Char(
        string="Lugar trabajo",
        store=True
    )
    nombre_establecimiento = fields.Char(
        string="Nombre establecimiento",
        store=True
    )
    razon_social = fields.Char(
        string="Razon social",
        store=True
    )
    direccion_comercial = fields.Char(
        string="Dirección comercial",
        store=True
    )