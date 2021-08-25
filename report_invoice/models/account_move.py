# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_create_user_id = fields.Many2one(comodel_name='res.users', string='Creador de cotización')
    sale_purchase_order = fields.Char(string='N° Orden de Compra')
    amount_discount = fields.Monetary(string='Descuento', readonly=True, store=True, compute='_compute_amount_discount', currency_field='company_currency_id')
    amount_without_discount_and_tax = fields.Monetary(string='Subtotal', store=True, readonly=True, compute='_compute_amount_discount', currency_field='company_currency_id')

    @api.depends('line_ids.debit', 'line_ids.credit', 'line_ids.currency_id', 'line_ids.amount_currency', 'line_ids.amount_residual', 'line_ids.amount_residual_currency', 'line_ids.payment_id.state')
    def _compute_amount_discount(self):
        for move in self:
            price_unit_wo_discount = 0
            for line in move.line_ids:
                price_unit_wo_discount += line.price_unit * line.quantity * (line.discount / 100.0)

            move.amount_discount = price_unit_wo_discount
            move.amount_without_discount_and_tax = move.amount_untaxed + price_unit_wo_discount


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    price_qty_amount = fields.Monetary(string='Importe', store=True, readonly=True, currency_field='always_set_currency_id')

    @api.model
    def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes, move_type):
        res = super(AccountMoveLine, self)._get_price_total_and_subtotal_model(price_unit, quantity, discount, currency, product, partner, taxes, move_type)
        res['price_qty_amount'] = price_unit * quantity
        return res
