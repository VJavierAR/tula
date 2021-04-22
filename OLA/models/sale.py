from odoo import models, fields, api,_
import datetime, time
from odoo import exceptions
import logging, ast
_logger = logging.getLogger(__name__)

class sale(models.Model):
	_inherit = 'sale.order'
	productos_sugeridos = fields.One2many('product.suggested','rel_id')
	arreglo = fields.Char(default='[]')
	#order_line = fields.One2many(comodel_name = 'sale.order.line', inverse_name = 'order_id', compute = 'precio_minimo')

	@api.onchange('arreglo')
	def addsegesst(self):
		if(self.arreglo!='[]'):
			data=eval(self.arreglo)
			dat=self.env['product.product'].browse(data)
			for d in dat:
				_logger.info(d.id)
				self.order_line.write({'product_id':d.id,'order_id':self.id,'product_uom_qty':1,'name':d.description,'price_unit':d.lst_price})

	# @api.onchange('productos_sugeridos')
	# def agregar(self):
	# 	if(len(self.productos_sugeridos)>0):			
	# 		for p in self.productos_sugeridos:

	@api.onchange('order_line')
	def comprobar_limite_de_credito(self):
		if len(self.order_line) > 0 and self.partner_id:
			total = self.amount_total
			limite_de_credito = self.partner_id.limite_credito
			_logger.info("total: " + str(total) + " limite de credito: " + str(limite_de_credito))

			genero_alertas = False

			title = "Alertas: "
			message = """Mensajes: \n"""

			# Comprobar precio minimo
			for linea in self.order_line:
				_logger.info("linea.price_unit: " + str(linea.price_unit))
				if linea.price_unit < linea.x_studio_field_Ml1CB:
					title = title + "Precio minímo de venta. | "
					message = message + """El producto: """ + str(
						linea.product_id.display_name) + """ esta rebasando su precio minímo de venta.\nPrecio: """ + str(
						linea.price_unit) + """\nPrecio minímo: """ + str(linea.x_studio_field_Ml1CB) + """\n"""
					genero_alertas = True
				# raise Warning('Estas rebasando tu precio minímo de venta')
				elif linea.price_subtotal < linea.x_studio_field_Ml1CB:
					title = title + "Precio minímo de venta. | "
					message = message + """El producto: """ + str(
						linea.product_id.display_name) + """ esta rebasando su precio minímo de venta.\nPrecio: """ + str(
						linea.price_subtotal) + """\nPrecio minímo: """ + str(linea.x_studio_field_Ml1CB) + """\n"""
					genero_alertas = True
			# raise Warning('Estas rebasando tu precio minímo de venta')

			#Caso en que excede limite de credito la linea de pediodo de venta
			if total > limite_de_credito:
				title = title + "Límite de crédito excedido. | "
				message = message + """Se excedio el límite de crédito: \n
								Límite de credito: $""" + str(limite_de_credito) + """\n
								Costo total: $""" + str(total) + """\n
						  """
				genero_alertas = True

			#Caso en que excede el limite de credito las facturas no pagadas y la linea de pedido de venta
			facturas_no_pagadas = self.sudo().env['account.move'].search(
				["&", "&",
				 ["invoice_payment_state", "=", "not_paid"],
				 ["state", "=", "posted"],
				 ["partner_id", "=", self.partner_id.id]
				 ]
			)
			_logger.info("facturas_no_pagadas: ")
			_logger.info(facturas_no_pagadas)
			if facturas_no_pagadas:
				total_de_facturas_no_pagadas = 0
				for factura_no_pagada in facturas_no_pagadas:
					total_de_facturas_no_pagadas = total_de_facturas_no_pagadas + factura_no_pagada.amount_total
				total_con_facturas = total + total_de_facturas_no_pagadas
				if total_con_facturas > limite_de_credito:
					title = title + "Límite de crédito excedido. | "
					message = message + """Se excedio el límite de crédito por facturas no pagadas y total del pedido de venta actual: \n
									Límite de credito: $""" + str(limite_de_credito) + """\n
									Costo total de pedido de venta actual: $""" + str(total) + """
									Costo total en facturas no pagadas: $""" + str(total_de_facturas_no_pagadas) + """\n
							  """
					genero_alertas = True

			if genero_alertas:
				return {
					#'value': {},
					'warning': {
						'title': title,
						'message': message
					}
				}





class saleOr(models.Model):
	_inherit='sale.order.line'
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


class sale_order_line(models.Model):
	_inherit = 'sale.order.line'

	x_studio_field_Ml1CB = fields.float("Precio minímo", compute="precio_minimo")

	@api.depends('price_unit')
	def precio_minimo(self):
		for rec in self:
			_logger.info("precio_minimo")
			genero_alertas = False

			title = "Alertas: "
			message = """Mensajes: \n"""

			# Comprobar precio minimo
			if rec.price_unit:
				_logger.info("linea.price_unit: " + str(rec.price_unit))
				if rec.price_unit < rec.x_studio_field_Ml1CB:
					title = title + "Precio minímo de venta. | "
					message = message + """El producto: """ + str(
						rec.product_id.display_name) + """ esta rebasando su precio minímo de venta.\nPrecio: """ + str(
						rec.price_unit) + """\nPrecio minímo: """ + str(rec.x_studio_field_Ml1CB) + """\n"""
					genero_alertas = True
				# raise Warning('Estas rebasando tu precio minímo de venta')
				elif rec.price_subtotal < rec.x_studio_field_Ml1CB:
					title = title + "Precio minímo de venta. | "
					message = message + """El producto: """ + str(
						rec.product_id.display_name) + """ esta rebasando su precio minímo de venta.\nPrecio: """ + str(
						rec.price_subtotal) + """\nPrecio minímo: """ + str(rec.x_studio_field_Ml1CB) + """\n"""
					genero_alertas = True
			# raise Warning('Estas rebasando tu precio minímo de venta')
			if genero_alertas:
				return {
					# 'value': {},
					'warning': {
						'title': title,
						'message': message
					}
				}

class productSuggested(models.Model):
	_name='product.suggested'
	_description='Productos sugeridos'
	product_rel=fields.Many2one('product.product')
	product_sug=fields.Many2one('product.product')
	rel_id=fields.Many2one('sale.order')
	agregar=fields.Boolean()
	bandera=fields.Integer(default=0)

	@api.depends('agregar')
	def add(self):
		if(self.agregar):
			self.bandera=self.bandera+1

			#self.rel_id.write({'arreglo':str([self.product_sug.id])})

	def add1(self):
		self.rel_id.order_line=[(0, 0, {'product_id':self.product_sug.id,'order_id':self.rel_id.id})]
