from odoo import models, fields, api,_
import logging, ast
_logger = logging.getLogger(__name__)


class product(models.Model):
	_inherit = 'product.template'

	codigo_producto_cliente = fields.Text(
		string = "Código de cliente",
		store = True,
		#track_visibility = 'onchange'
	)

	@api.model
	def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
		args = args or []
		recs = self.browse()
		if not recs:
			recs = self.search(['|', '|', '|',
								('name', operator, name),
								('default_code', operator, name),
								('codigo_producto_cliente', operator, name),
								('barcode', operator, name)
								] + args, limit=limit)
		return recs.name_get()


class productPr(models.Model):
	_inherit = 'product.product'
	sug_rel=fields.Many2many('product.product',relation='product_may_sug',column1='id', column2='id2')

	@api.model
	def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
		args = args or []
		recs = self.browse()
		if not recs:
			recs = self.search(['|', '|', '|',
								('name', operator, name),
								('default_code', operator, name),
								('codigo_producto_cliente', operator, name),
								('barcode', operator, name)
								] + args, limit=limit)
		return recs.name_get()