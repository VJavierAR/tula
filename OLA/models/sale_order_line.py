from odoo import models, fields, api,_
import datetime, time
from odoo import exceptions
from odoo.exceptions import AccessDenied
import logging, ast
_logger = logging.getLogger(__name__)

class saleOr(models.Model):
	_inherit='sale.order.line'

	bloqueo = fields.Boolean(
		string = 'Bloqueo por límite de descuento',
		default = False
	)
	existencias = fields.Char()


	@api.onchange("product_id")
	def product_id_change(self):
		res = super(saleOr, self).product_id_change()
		if not self.product_id:  # pragma: no cover
			return res
		##if not self.order_partner_id:
		##	return res
		##if not self.product_id.codigos_de_producto:
		##	return res
		##if not self.order_id.partner_id:
		##	return res
		producto = self.product_id
		codigo_final = "[" + str(producto.default_code) + "] " + str(producto.name)
		cliente = self.order_id.partner_id
		if cliente.id:
			codigos_por_cliente = self.product_id.codigos_de_producto
			if codigos_por_cliente.ids:
				for codigo in codigos_por_cliente:
					if codigo.cliente.id == cliente.id:
						codigo_final = "[" + str(codigo.codigo_producto) + "] " + str(producto.name)
						break
		self.name = codigo_final
		#self.order_line =
		return res

		"""
		if (
				self.user_has_groups(
					"sale_order_line_description."
					"group_use_product_description_per_so_line"
				)
				and self.product_id.description_sale
		):
			product = self.product_id
			if self.order_id.partner_id:
				product = product.with_context(lang=self.order_id.partner_id.lang, )
			self.name = product.description_sale
		return res
		"""


	#@api.onchange('product_id')
	def buscaProductos(self):                                        
	    ft=''
	    cabecera='<table><tr><th>Compañia</th><th>Cantidad</th></tr>'
	    for cal in self.product_id.sudo().stock_quant_ids.filtered(lambda x:x.company_id.id!=False and x.quantity>=0):   
	        ft='<tr><td>'+str(cal.company_id.name)+'</td><td>'+str(cal.quantity)+'</td></tr>'+ft
	    tabla=cabecera+ft+'</table>'
	    self.existencias=str(tabla)


	@api.onchange('product_id')
	def stock(self):
		res={}
		if(self.product_id.qty_available<=0):
			pa=self.product_id.mapped('alt_rel.id')
			po=self.env['product.product'].browse(pa)
			po1=po.filtered(lambda x:x.qty_available>0)
			if(po1.mapped('id')!=[]):
				res['domain']={'product_id':[['id','in',po1.mapped('id')]]}
				return res

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
			raise AccessDenied(
				_(message))
			"""
			return {
				# 'value': {},
				'warning': {
					'title': title,
					'message': message
				}
			}
			"""
