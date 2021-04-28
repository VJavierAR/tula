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
	alt_rel=fields.Many2many('product.product',relation='product_alte_rel',column1='id', column2='id2')

	codigos_de_producto = fields.One2many(
		comodel_name='product.codigos',
		inverse_name = 'producto_id',
		string = 'Códigos de producto'
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

class codigos(models.Model):
	_name='product.codigos'
	_description='Lista de codigos para los clientes'

	producto_id = fields.Many2one(
		comodel_name = 'product.product',
		string = 'Producto relacionado'
	)
	cliente = fields.Many2one(
		comodel_name = 'res.partner',
		string = 'Cliente',
		domain = '',
		track_visibility = 'onchange'
	)

	codigo_producto = fields.Text(
		string = "Código de producto",
		store = True,
		track_visibility = 'onchange'
	)
