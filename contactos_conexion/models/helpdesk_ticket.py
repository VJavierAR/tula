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


class SaleOrder(models.Model):
    _inherit = 'helpdesk.ticket'
    _description = 'Cambios'

    origen_sale = fields.Many2one(
        comodel_name='sale.order',
        string='Pedidod de venta origen'
    )
    origin_crm = fields.Char(related='partner_id.oprotunidad_origen',string='Oportunidad origen')
    def visible(self):
        self.partner_id.write({'active':True})