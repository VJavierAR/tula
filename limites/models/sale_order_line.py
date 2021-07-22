from odoo import models, fields, api,_
import datetime, time
from odoo import exceptions
from odoo.exceptions import AccessDenied
import logging, ast
_logger = logging.getLogger(__name__)


class saleOr(models.Model):
	_inherit='sale.order.line'

	bloqueo = fields.Boolean(
		string='Bloqueo por límite de descuento',
		default=False
	)
	existencias = fields.Char(
		string="Almacén/Cantidad",
		store=True
	)
	coste_producto = fields.Float(
		string="Coste",
		store=True,
		related="product_id.standard_price"
	)
	purchase_price = fields.Float(
		string="Coste",
		store=True,
		copy=True,
	)

	existencias_check = fields.Boolean(
		string="Mostrar existencias",
		default=False
	)

	@api.onchange('price_unit', 'discount')
	def precio_minimo(self):
		d = self.env.user.max_discount
		descuento_cliente = self.order_partner_id.limite_de_descuento
		if descuento_cliente > d:
			if self.discount > descuento_cliente:
				self.bloqueo = True
			else:
				self.bloqueo = False
		else:
			if self.discount > d:
				self.bloqueo = True
			else:
				self.bloqueo = False

		genero_alertas = False
		title = "Alertas: "
		message = """Mensajes: \n"""

		# Comprobar precio minimo

		# if self.price_unit and self.product_id.id:
		#	if self.price_unit < self.x_studio_precio_mnimo:
		#		title = title + "Precio minímo de venta. | "
		#		message = message + """El producto: """ + str(
		#			self.product_id.display_name) + """ esta rebasando su precio minímo de venta.\nPrecio: """ + str(
		#			self.price_unit) + """\nPrecio minímo: """ + str(self.x_studio_precio_mnimo) + """\n"""
		#		genero_alertas = True

		#	elif self.price_subtotal < self.x_studio_precio_mnimo:
		#		title = title + "Precio minímo de venta. | "
		#		message = message + """El producto: """ + str(
		#			self.product_id.display_name) + """ esta rebasando su precio minímo de venta.\nPrecio: """ + str(
		#			self.price_subtotal) + """\nPrecio minímo: """ + str(self.x_studio_precio_mnimo) + """\n"""
		#		genero_alertas = True

		if genero_alertas:
			raise AccessDenied(
				_(message))