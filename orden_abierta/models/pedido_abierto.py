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
        comodel_name="pedido.abierto.linea",
        inverse_name="pedido_abierto_rel",
        string="Lineas de pedido abierto",
        store=True
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
    id_orden_temp = fields.Integer(
        string="id orden temp",
        store=True
    )
    pedido_cliente = fields.Char(
        string="Pedido cliente",
        store=True,
        help="Actualiza el dato pedido cliente de todas las lineas de pedido"
    )
    plazo_de_pago = fields.Many2one(
        comodel_name="account.payment.term",
        string="Plazo de pago",
        # compute="_compute_plazo_de_pago",
        store=True
        # default=lambda self: self.partner_id.property_payment_term_id.id or False
    )
    pricelist_id = fields.Many2one(
        'product.pricelist', string='Pricelist', check_company=True,  # Unrequired company
        required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="If you change the pricelist, only newly added lines will be affected.")
    currency_id = fields.Many2one(
        "res.currency",
        related='pricelist_id.currency_id',
        string="Currency",
        readonly=True,
        required=True
    )

    @api.depends('lineas_pedido.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.lineas_pedido:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    amount_untaxed = fields.Monetary(
        string='Untaxed Amount',
        store=True,
        readonly=True,
        compute='_amount_all',
        tracking=5
    )
    amount_tax = fields.Monetary(
        string='Taxes',
        store=True,
        readonly=True,
        compute='_amount_all'
    )
    amount_total = fields.Monetary(
        string='Total',
        store=True,
        readonly=True,
        compute='_amount_all',
        tracking=4
    )

    @api.depends('partner_id')
    def _compute_plazo_de_pago(self):
        for rec in self:
            if rec.partner_id.id:
                rec.plazo_de_pago = rec.partner_id.property_payment_term_id.id

    @api.onchange('partner_id')
    def actualiza_cliente_en_lineas(self):
        if self.partner_id.id and self.lineas_pedido.ids:
            for linea in self.lineas_pedido:
                linea.order_partner_id = self.partner_id.id
            # if self.partner_id.property_payment_term_id.id:
            #    self.plazo_de_pago = self.partner_id.property_payment_term_id.id

        self.plazo_de_pago = self.partner_id.property_payment_term_id.id or False
        self.pricelist_id = self.partner_id.property_product_pricelist.id or False

    @api.onchange('pedido_cliente')
    def actualiza_pedido_cliente_en_lienas(self):
        if self.pedido_cliente and self.lineas_pedido.ids:
            for linea in self.lineas_pedido:
                linea.pedido_cliente = self.pedido_cliente

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('pedido.abierto.seq') or 'New'

        if 'pedido_cliente' in vals and 'lineas_pedido' in vals:
            for linea in vals.get('lineas_pedido'):
                linea[2]['pedido_cliente'] = vals['pedido_cliente']
        """                
        if 'partner_id' in vals and 'plazo_de_pago' not in vals:
            cliente = self.env['res.partner'].search([
                ('id', '=', vals['partner_id'])
            ])
            vals['plazo_de_pago'] = cliente.property_payment_term_id.id
        """

        """
        if 'lineas_pedido' in vals:
            orden_temp = self.env['sale.order'].create({
                'partner_id': vals.get('partner_id'),
                'active': False
            })
            vals['id_orden_temp'] = orden_temp.id

            for linea in vals.get('lineas_pedido'):
                linea[2]['order_id'] = orden_temp.id
        """

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

        for linea in wiz.lineas_pedidos:
            if linea.linea_confirmada:
                wiz.write({
                    'lineas_pedidos': [(3, linea.id, 0)]
                })
                # linea.unlink()

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

    def get_sales_directas(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pedidos directos',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [
                ('pedido_abierto_origen', '=', self.id),
            ],
            'context': "{'create': False}"
        }

    def get_lineas_abiertas(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Líneas de pedido abierto',
            'view_mode': 'tree',
            'res_model': 'pedido.abierto.linea',
            'domain': [
                ('pedido_abierto_rel', '=', self.id),
            ],
            'context': "{'create': False}"
        }
