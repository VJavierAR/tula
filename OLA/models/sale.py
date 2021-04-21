from odoo import models, fields, api,_


class sale(models.Model):
	_inherit='sale.order'
	productos_sugeridos=fields.One2many('product.suggested','rel_id')

class saleOr(models.Model):
	_inherit='sale.order.line'

	@api.onchange('product_id')
	def addSugges(self):
		p=self.product_id.mapped('sug_rel.id')
		for pi in p:
			self.order_id.write({'productos_sugeridos':self.product_id.id,'product_sug':pi})


class productSuggested(models.Model):
	_name='product.suggested'
	_description='Productos sugeridos'
	product_rel=fields.Many2one('product.product')
	product_sug=fields.Many2one('product.product')
	rel_id=fields.Many2one('sale.order')

	def add(self):
		self.rel_id.order_line.write({(0, 0, {'product_id':self.product_sug.id })})

