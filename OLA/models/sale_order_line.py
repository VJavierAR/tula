from odoo import models, fields, api,_
import datetime, time
from odoo import exceptions
import logging, ast
_logger = logging.getLogger(__name__)

class saleOr(models.Model):
	_inherit='sale.order.line'

	bloqueo = fields.Boolean(
		string = 'Bloqueo por límite de descuento',
		default = False
	)

	# @api.onchange('product_id')
	# def stock(self):
	# 	res={}
	# 	if(self.product_id.qty_available<=0):
	# 		pa=self.product_id.mapped('alt_rel.id')
	# 		po=self.env['product.product'].browse(pa)
	# 		po1=po.filtered(lambda x:x.qty_available>0)
	# 		if(po1.mapped('id')!=[]):
	# 			res['domain']={'product_id':[['id','in',po1.mapped('id')]]}
	# 			return res
	# def addSugges(self):
	# 	p=self.product_id.mapped('sug_rel.id')
	# 	arreglo=[]
	# 	_logger.info(str(p))
	# 	for pi in p:
	# 		pro=dict()
	# 		pro['product_rel']=self.product_id.id
	# 		pro['product_sug']=pi
	# 		pro['rel_id']=self.order_id.id
	# 		arreglo.append(pro)
	# 		_logger.info(str(pi))
	# 	self.order_id.productos_sugeridos.write(arreglo)

	x_studio_field_Ml1CB = fields.Float("Precio minímo", related="product_id.standard_price")

	@api.onchange('price_unit', 'discount')
	def precio_minimo(self):
		d=self.env.user.max_discount
		if(self.discount>d):
			self.bloqueo=True
		if(self.discount<=d):
			self.bloqueo=False
			
		genero_alertas = False

		title = "Alertas: "
		message = """Mensajes: \n"""

		# Comprobar precio minimo
		if self.price_unit and self.product_id.id:
			if self.price_unit < self.x_studio_precio_mnimo:
				title = title + "Precio minímo de venta. | "
				message = message + """El producto: """ + str(
					self.product_id.display_name) + """ esta rebasando su precio minímo de venta.\nPrecio: """ + str(
					self.price_unit) + """\nPrecio minímo: """ + str(self.x_studio_precio_mnimo) + """\n"""
				genero_alertas = True

			elif self.price_subtotal < self.x_studio_precio_mnimo:
				title = title + "Precio minímo de venta. | "
				message = message + """El producto: """ + str(
					self.product_id.display_name) + """ esta rebasando su precio minímo de venta.\nPrecio: """ + str(
					self.price_subtotal) + """\nPrecio minímo: """ + str(self.x_studio_precio_mnimo) + """\n"""
				genero_alertas = True

		if genero_alertas:
			return {
				# 'value': {},
				'warning': {
					'title': title,
					'message': message
				}
			}