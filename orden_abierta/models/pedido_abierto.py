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
            ('confirmado', 'confirmado'),
            ('expirado', 'expirado')
        ],
        string="Estados",
        readonly=True,
        default="borrador"
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
        # states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="If you change the pricelist, only newly added lines will be affected."
    )
    name = fields.Char(
        string='Order Reference',
        required=True,
        copy=False,
        readonly=True,
        states={'borrador': [('readonly', False)]},
        index=True,
        default=lambda self: _('New')
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Comercial',
        index=True,
        tracking=2,
        default=lambda self: self.env.user,
        domain=lambda self: [('groups_id', 'in', self.env.ref('sales_team.group_sale_salesman').id)]
    )
    pedidos_directos = fields.One2many(
        comodel_name="sale.order",
        inverse_name="pedido_abierto_origen",
        string="Pedidos directos"
    )

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('pedido.abierto.seq') or 'New'

        _logger.info("vals: \n" + str(vals))
        orden_temp = self.env['sale.order'].create({
            'partner_id': vals.get('partner_id'),
            'active': False
        })
        _logger.info("vals.get('lineas_pedido'): \n" + str(vals.get('lineas_pedido')))
        for linea in vals.get('lineas_pedido'):
            linea['order_id'] = orden_temp.id

        result = super(PedidoAbierto, self).create(vals)
        return result

    def crear_pedido_wizard(self):
        wiz = self.env['pedido.abierto.wizard'].create({
            'pedido_abierto_id': self.id
        })
        _logger.info("self.lineas_pedido.ids: " + str(self.lineas_pedido.ids))
        _logger.info("self.lineas_pedido.pedido_abierto_rel: " + str(self.lineas_pedido.mapped('pedido_abierto_rel')))
        wiz.write({
            'lineas_pedidos': [(6, 0, self.lineas_pedido.ids)]
        })

        view = self.env.ref('orden_abierta.view_pedido_abierto_wizard')
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
            # 'context': {'default_lineas_pedidos': [(6, 0, self.lineas_pedido.ids)]},
        }
