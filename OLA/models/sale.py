from odoo import models, fields, api,_
import datetime, time
from odoo import exceptions
import logging, ast
_logger = logging.getLogger(__name__)

class sale(models.Model):
	_inherit='sale.order'
	productos_sugeridos=fields.One2many('product.suggested','rel_id')

class saleOr(models.Model):
	_inherit='sale.order.line'

	@api.onchange('product_id')
	def addSugges(self):
		p=self.product_id.mapped('sug_rel.id')
		_logger.info(str(p))
		for pi in p:
			_logger.info(str(pi))
			self.order_id.productos_sugeridos=[{'product_rel':self.product_id.id,'product_sug':pi}]


class productSuggested(models.Model):
	_name='product.suggested'
	_description='Productos sugeridos'
	product_rel=fields.Many2one('product.product')
	product_sug=fields.Many2one('product.product')
	rel_id=fields.Many2one('sale.order')

	def add(self):
		self.rel_id.order_line.write({(0, 0, {'product_id':self.product_sug.id })})

