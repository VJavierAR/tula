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

	@api.onchange("product_id")
	def product_id_change(self):
		res = super(saleOr, self).product_id_change()
		if not self.product_id:  # pragma: no cover
			return res
		producto = self.product_id
		codigo_final = str(producto.display_name)
		cliente = self.order_id.partner_id
		if cliente.id:
			codigos_por_cliente = self.product_id.codigos_de_producto
			if codigos_por_cliente.ids:
				for codigo in codigos_por_cliente:
					if codigo.cliente.id == cliente.id:
						codigo_final = "[" + str(codigo.codigo_producto) + "] " + str(producto.name)
						break
		self.name = codigo_final
		return res

	def mostrar_existencias(self):
		_logger.info("self.product_id.id: " + str(self.product_id.id))
		if self.product_id.id:
			ft = ''
			cabecera = '<table class="table"><thead><tr><th scope="col">Almacén</th> <th scope="col">Cantidad</th></tr></thead><tbody>'
			for cal in self.product_id.sudo().stock_quant_ids.filtered(
					lambda x: x.company_id.id != False and x.quantity >= 0 and x.location_id.usage == 'internal'):
				ft += '<tr><td>' + str(cal.location_id.display_name) + '</td><td>' + str(
					cal.quantity) + '</td></tr>'
			tabla = cabecera + ft + '</tbody></table>'
			# self.existencias = str(tabla)
			view = self.env.ref('OLA.sale_order_existencias_view')
			wiz = self.env['sale.order.existencias'].create({'mensaje': str(tabla)})
			return {
				'alerta': True,
				'name': _('Existencias'),
				'type': 'ir.actions.act_window',
				'view_mode': 'form',
				'res_model': 'sale.order.existencias',
				'views': [(view.id, 'form')],
				'view_id': view.id,
				'target': 'new',
				'res_id': wiz.id,
				'context': self.env.context,
			}

	@api.onchange('existencias_check')
	def mostrar_existencias_check(self):
		_logger.info("self.existencias_check: " + str(self.existencias_check))
		if self.existencias_check and self.product_id.id:
			#self.mostrar_existencias()
			cabecera = "Bodega : Cantidad"
			ft = ''
			for cal in self.product_id.sudo().stock_quant_ids.filtered(
					lambda x: x.company_id.id != False and x.quantity >= 0 and x.location_id.usage == 'internal'):
				ft += str(cal.location_id.display_name) + ': ' + str(cal.quantity) + '\n'

			self.existencias_check = False
			return {
				'warning': {
					'title': "Existencias",
					'message': str(ft)
				},
			}

	@api.onchange('product_id')
	def buscaProductos(self):
		"""
		if self.product_id.id:
			ft = ''
			cabecera = '<table><tr><th>Bodega</th><th>Cantidad</th></tr>'
			for cal in self.product_id.sudo().stock_quant_ids.filtered(lambda x:x.company_id.id!=False and x.quantity>=0 and x.location_id.usage=='internal'):
				ft = '<tr><td>'+str(cal.location_id.display_name)+'</td><td>'+str(cal.quantity)+'</td></tr>'+ft
			tabla = cabecera+ft+'</table>'
			self.existencias = str(tabla)
		"""
		if self.product_id.id:
			ft = ''
			for cal in self.product_id.sudo().stock_quant_ids.filtered(
					lambda x: x.company_id.id != False and x.quantity >= 0 and x.location_id.usage == 'internal'):
				ft += str(cal.location_id.display_name) + ': ' + str(cal.quantity) + '\n'
			self.existencias = str(ft)


	@api.onchange('product_id')
	def stock(self):
		res = {}
		if self.product_id.id and self.product_id.qty_available <= 0:
			pa = self.product_id.mapped('alt_rel.id') + self.product_id.product_tmpl_id.mapped('alt_rel.id')
			po = self.env['product.product'].browse(pa)
			po1 = po.filtered(lambda x: x.qty_available > 0)
			if po1.mapped('id') != []:
				res['domain'] = {
					'product_id': [
						['id', 'in', po1.mapped('id')]
					]
				}
				return res

	x_studio_field_Ml1CB = fields.Float("Precio minímo", related="product_id.standard_price")

	@api.onchange('price_unit', 'discount','product_uom_qty')
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
		if self.price_unit and self.product_id.id:
			if(self.product_uom_qty<1):
				calculo=self.x_studio_precio_mnimo/self.product_uom_qty
				if(self.price_subtotal<calculo):
					title = title + "Precio minímo de venta. | "
					message = message + """El producto: """ + str(
						self.product_id.display_name) + """ esta rebasando su precio minímo de venta.\nPrecio: """ + str(
						self.price_unit) + """\nPrecio minímo: """ + str(self.x_studio_precio_mnimo) + """\n"""
					genero_alertas = True
			else:	
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