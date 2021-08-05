# -*- coding: utf-8 -*-

from odoo import models, fields, api
from email.utils import formataddr
from odoo.exceptions import UserError, RedirectWarning
from odoo import exceptions, _
from dateutil.relativedelta import relativedelta
import logging, ast
import datetime, time
import pytz
import base64
import requests
_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = 'res.partner'
    _description = 'Cambios'

    @api.model
    def create(self, vals):
        _logger.info("valores al crear desde crm: \n" + str(vals))
        _logger.info("self: \n" + str(self))
        rec = super(Partner, self).create(vals)

        self.env['crm.lead'].search([
            ('partner_id', '=', ''),
        ])

        return rec