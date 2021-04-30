# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import UserError


class StockPickingPrint(models.TransientModel):
    _name = 'stock.picking.print'

    user_pin = fields.Char(string='Pin de usuario', required=True)

    def button_print(self):
        user_id = self.env['res.users'].search([('user_pin', '=', self.user_pin)], limit=1)
        if self.env.user.id == user_id.id:
            active_id = self.env.context['active_id']
            picking = self.env['stock.picking'].search([('id', '=', active_id)], limit=1)
            if picking.state != 'done':
                picking.state = 'printed'
            # picking.message_post(body=("Impresión realizada."))
            picking.user_print_id = self.env.user.id
            return picking.do_print_picking()
        else:
            raise UserError("El pin no es válido para el usuario actual.")


class StockPickingValidate(models.TransientModel):
    _name = 'stock.picking.validate'

    user_pin = fields.Char(string='Pin de usuario', required=True)

    def button_validate(self):
        user_id = self.env['res.users'].search([('user_pin', '=', self.user_pin)], limit=1)
        if self.env.user.id == user_id.id:
            active_id = self.env.context['active_id']
            picking = self.env['stock.picking'].search([('id', '=', active_id)], limit=1)
            picking.button_validate()
            picking.user_validate_id = self.env.user.id
            # picking.message_post(body=("Validación realizada."))
            return {'type': 'ir.actions.act_window_close'}
        else:
            raise UserError("El pin no es válido para el usuario actual.")
