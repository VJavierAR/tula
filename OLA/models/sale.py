from odoo import models, fields, api,_
import datetime, time
from odoo import exceptions
import logging, ast
_logger = logging.getLogger(__name__)

class sale(models.Model):
	_inherit='sale.order'
	productos_sugeridos=fields.One2many('product.suggested','rel_id')

	@api.onchange('order_line')
	def funct(self):
		if(len(self.order_line)>0):
			arreglo=[]
			self.productos_sugeridos=[(5,0,0)]
			p=self.order_line.mapped('product_id.sug_rel.id')
			for pii in self.order_line:
				pro={}
				pro['product_rel']=pii.product_id.id
				p=pii.mapped('product_id.sug_rel.id')
				for pi in p:
					pro['product_sug']=pi
					pro['rel_id']=self.id
					self.productos_sugeridos=[(0,0,pro)]
					arreglo.append(pro)
			_logger.info(str(arreglo))
			#self.productos_sugeridos=arreglo

	@api.onchange('order_line')
	def comprobar_limite_de_credito(self):
		_logger.info("self.order_line.ids: " + str(self._origin.order_line.ids))
		if self._origin.order_line.ids:
			total = self.amount_total
			limite_de_credito = self.partner_id.limite_credito
			_logger.info("total: " + str(total) + " limite de credito: " + str(limite_de_credito))

			#Caso en que excede limite de credito la linea de pediodo de venta
			if total > limite_de_credito:
				title = "Límite de crédito excedido."
				message = """Se excedio el límite de crédito: \n
								Límite de credito: $""" + str(limite_de_credito) + """\n
								Costo total: $""" + str(total) + """
						  """
				return {
					'value': {},
					'warning': {
						'title': title,
						'message': message
					}
				}

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
					title = "Límite de crédito excedido."
					message = """Se excedio el límite de crédito por facturas no pagadas y total del pedido de venta actual: \n
													Límite de credito: $""" + str(limite_de_credito) + """\n
													Costo total de pedido de venta actual: $""" + str(total) + """
													Costo total en facturas no pagadas: $""" + str(total_de_facturas_no_pagadas) + """
											  """
					return {
						'value': {},
						'warning': {
							'title': title,
							'message': message
						}
					}


class saleOr(models.Model):
	_inherit='sale.order.line'

	# @api.onchange('product_id')
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


class productSuggested(models.Model):
	_name='product.suggested'
	_description='Productos sugeridos'
	product_rel=fields.Many2one('product.product')
	product_sug=fields.Many2one('product.product')
	rel_id=fields.Many2one('sale.order')

	def add(self):
		self.rel_id.order_line=[(0, 0, {'product_id':self.product_sug.id,'order_id':self.rel_id.id})]

