# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import logging, ast
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError
from statistics import mean
from collections import defaultdict
from odoo.tools import float_compare, float_round, float_is_zero, OrderedSet

class StockMove(models.Model):
	_inherit='stock.move'
	precio_impuesto=fields.Float()
	utilidad_venta=fields.Float()
	precio_lista=fields.Float()


	def product_price_update_before_done(self, forced_qty=None):
		tmpl_dict = defaultdict(lambda: 0.0)
		# adapt standard price on incomming moves if the product cost_method is 'average'
		std_price_update = {}
		for move in self.filtered(lambda move: move._is_in() and move.with_context(force_company=move.company_id.id).product_id.cost_method == 'average'):
			product_tot_qty_available = move.product_id.sudo().with_context(force_company=move.company_id.id).quantity_svl + tmpl_dict[move.product_id.id]
			rounding = move.product_id.uom_id.rounding

			valued_move_lines = move._get_in_move_lines()
			qty_done = 0
			for valued_move_line in valued_move_lines:
			    qty_done += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done, move.product_id.uom_id)

			qty = forced_qty or qty_done
			if float_is_zero(product_tot_qty_available, precision_rounding=rounding):
				new_std_price = move._get_price_unit()
			elif float_is_zero(product_tot_qty_available + move.product_qty, precision_rounding=rounding) or \
					float_is_zero(product_tot_qty_available + qty, precision_rounding=rounding):
				new_std_price = move._get_price_unit()
			else:
				# Get the standard price
				amount_unit = std_price_update.get((move.company_id.id, move.product_id.id)) or move.product_id.with_context(force_company=move.company_id.id).standard_price
				new_std_price = ((amount_unit * product_tot_qty_available) + (move._get_price_unit() * qty)) / (product_tot_qty_available + qty)

			tmpl_dict[move.product_id.id] += qty_done
			# Write the standard price, as SUPERUSER_ID because a warehouse manager may not have the right to write on products
			d={'standard_price': new_std_price}
			if(move.purchase_line_id.precio_impuesto!=0 or move.purchase_line_id.precio_lista!=0 or move.purchase_line_id.utilidad_venta!=0):
				d['precio_impuesto']=move.purchase_line_id.precio_impuesto
				d['precio_lista']=move.purchase_line_id.precio_lista
				d['utilidad_venta']=move.purchase_line_id.utilidad_venta
			move.product_id.with_context(force_company=move.company_id.id).sudo().write(d)
			std_price_update[move.company_id.id, move.product_id.id] = new_std_price
