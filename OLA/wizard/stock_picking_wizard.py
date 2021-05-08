# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import UserError


class StockPickingPrint(models.TransientModel):
    _name = 'stock.picking.print'

    user_pin = fields.Char(string='Pin de usuario')
    picking = fields.Many2one('stock.picking')
    def button_print(self):
        user_id = self.env['res.users'].search([('user_pin', '=', self.user_pin)], limit=1)
        if self.env.user.id == user_id.id:
            if self.picking.state != 'done':
                self.picking.state = 'printed'
            self.picking.user_print_id = self.env.user.id
            return self.picking.do_print_picking()
        else:
            raise UserError("El pin no es válido para el usuario actual.")


class StockPickingValidate(models.TransientModel):
    _name = 'stock.picking.validate'

    user_pin = fields.Char(string='Pin de usuario')
    picking = fields.Many2one('stock.picking')
    
    def button_validate(self):
        user_id = self.env['res.users'].search([('user_pin', '=', self.user_pin)], limit=1)
        if self.env.user.id == user_id.id:
            self.picking.user_validate_id = self.env.user.id
            # picking.message_post(body=("Validación realizada."))
            return self.picking.button_validate(True)
        else:
            raise UserError("El pin no es válido para el usuario actual.")
