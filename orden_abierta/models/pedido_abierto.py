# -*- coding: utf-8 -*-

from odoo import models, fields, api
from email.utils import formataddr
from odoo.exceptions import UserError, RedirectWarning
from odoo import exceptions, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging, ast
import pytz
import base64
import requests
import json

_logger = logging.getLogger(__name__)


class PedidoAbierto(models.Model):
    _name = 'pedido.abierto'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Genera pedido con base a lineas de pedido abierto'

    lineas_pedido = fields.One2many(
        comodel_name="sale.order.line",
        inverse_name="pedido_abierto_rel",
        string="Lineas de pedido abierto"
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Cliente"
    )
    state = fields.Selection(
        selection=[
            ('borrador', 'borrador'),
            ('abierto', 'abierto'),
            ('expirado', 'expirado')
        ],
        string="Estados"
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañia',
        required=True,
        index=True,
        default=lambda self: self.env.company
    )
    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string='Pricelist',
        check_company=True,  # Unrequired company
        # required=True,
        readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="If you change the pricelist, only newly added lines will be affected.")

    def crear_pedido_wizard(self):
        wiz = self.env['pedido.abierto.wizard'].create({
            'pedido_abierto_id': self.id
        })
        wiz.lineas_pedidos = [(6, 0, self.lineas_pedido.ids)]

        view = self.env.ref('orden_abierta.view_pdf_report')
        return {
            'name': _('Crear pedido '),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'pedido.abierto.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }
