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


class SaleOrderOrdenAbierta(models.Model):
    _inherit = 'sale.order'
    _description = 'Orden abierta'

    def conf(self):
        self.action_confirm()