# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'res.company'

    invoice_bank_accounts = fields.Text(string='Cuentas bancarias de factura')
    invoice_conditions = fields.Text(string='Condiciones de factura')
