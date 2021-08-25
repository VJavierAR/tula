# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import logging, ast
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError
from statistics import mean

class Compra(models.Model):
	_inherit='purchase.order'
	check=fields.Boolean(default=False)

	def boton_confirmar(self):
		self.button_confirm()
		if(self.check==False):
			for line in self.order_line:
				line.product_id.write({'nuevo_costo_facturacion_impuesto':0})
		if(self.picking_type_id.warehouse_id.auto_recepcion):
			sta = self.picking_ids.mapped('state')
			for pi in self.picking_ids.filtered(lambda x:x.state!='cancel'):
				if pi.state == 'assigned':
					pi.action_confirm()
					pi.move_lines._action_assign()
					pi.action_assign()
					return pi.button_validate()
				if pi.state in ('waiting','confirmed'):
					view = self.env.ref('orden_compra.purchase_order_alerta_view')
					wiz = self.env['purchase.order.alerta'].create({'mensaje': 'Sin stock disponible'})
					return {
						'alerta': True,
						'name': _('Alerta'),
						'type': 'ir.actions.act_window',
						'view_mode': 'form',
						'res_model': 'purchase.order.alerta',
						'views': [(view.id, 'form')],
						'view_id': view.id,
						'target': 'new',
						'res_id': wiz.id,
						'context': self.env.context,
					}
class CompraLine(models.Model):
	_inherit='purchase.order.line'
	precio_impuesto=fields.Float(default=0)
	utilidad_venta=fields.Float(default=0)
	precio_lista=fields.Float(default=0)