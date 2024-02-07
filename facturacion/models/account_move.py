# -*- coding: utf-8 -*-
from odoo import fields, models, api,_
from odoo.exceptions import UserError,AccessDenied,RedirectWarning
import logging, ast
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    tramite = fields.Selection(
        string='Estado Tramite',
        selection=[('tramitadas', 'tramitadas')]
    )

    tramite_seq = fields.Char(
        string="Secuencia de tramite",
        readonly=True,
        copy=False,
    )
