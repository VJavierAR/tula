#-*- coding: utf-8 -*-

from odoo import models, fields, api


class facturable(models.Model):
    _inherit = 'sale.order.line'
    facturable=fields.Float('Facturable')

class facturable(models.Model):
    _inherit = 'stock.picking'
    
    def write(self, vals):
        if vals.get('picking_type_id') and self.state != 'draft':
            raise UserError(_("Changing the operation type of this record is forbidden at this point."))
        # set partner as a follower and unfollow old partner
        if vals.get('partner_id'):
            for picking in self:
                if picking.location_id.usage == 'supplier' or picking.location_dest_id.usage == 'customer':
                    if picking.partner_id:
                        picking.message_unsubscribe(picking.partner_id.ids)
                    picking.message_subscribe([vals.get('partner_id')])
        res = super(Picking, self).write(vals)
        # Change locations of moves if those of the picking change
        after_vals = {}
        if vals.get('location_id'):
            after_vals['location_id'] = vals['location_id']
        if vals.get('location_dest_id'):
            after_vals['location_dest_id'] = vals['location_dest_id']
        if after_vals:
            self.mapped('move_lines').filtered(lambda move: not move.scrapped).write(after_vals)
        if vals.get('move_lines'):
            # Do not run autoconfirm if any of the moves has an initial demand. If an initial demand
            # is present in any of the moves, it means the picking was created through the "planned
            # transfer" mechanism.
            pickings_to_not_autoconfirm = self.env['stock.picking']
            for picking in self:
                if picking.state != 'draft':
                    continue
                for move in picking.move_lines:
                    if not float_is_zero(move.product_uom_qty, precision_rounding=move.product_uom.rounding):
                        pickings_to_not_autoconfirm |= picking
                        break
            (self - pickings_to_not_autoconfirm)._autoconfirm_picking()
        if('state' in vals):
        	if(vals['state']=='done'):
        		pass	
        return res
