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


class ResCompany(models.Model):
    _inherit = 'res.company'
    _description = 'Cambios'

    no_cia = fields.Char(
        string="No Cia",
        store=True,
        company_dependent=True,
        check_company=True
    )
