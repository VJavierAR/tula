from odoo import models, fields, api,_


class product(models.Model):
	_inherit = 'product.template'

	codigo_producto_cliente = fields.Text(
		string = "Código de cliente",
		store = True,
		#track_visibility = 'onchange'
	)

class productPr(models.Model):
	_inherit = 'product.product'
	sugerido=fields.Many2many('product.product')