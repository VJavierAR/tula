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
    _inherit = 'crm.'
    _description = 'Cambios'

    def conect(self):
        task = {"username": "apiodoo@promed-sa.com", "password": "ApiOdoo*001"}
        resp = requests.post('https://trxk539p2e.execute-api.us-east-1.amazonaws.com/prueba/Login', json=task)
        if resp.status_code == 200:
            _logger.info(resp)
            json_respuesta = resp.json()
            _logger.info(json_respuesta)

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
