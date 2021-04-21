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

	def addComa(snum):
		"Adicionar comas como separadores de miles a n. n debe ser de tipo string"
		s = snum;
		i = s.index('.')  # Se busca la posición del punto decimal
		while i > 3:
			i = i - 3
			s = s[:i] + ',' + s[i:]
		return s

	@api.onchange('order_line')
	def comprobar_limite_de_credito(self):
		if self.order_line.ids:
			total = self.amount_total
			limite_de_credito = self.partner_id.limite_credito
			_logger.debug("total: " + str(total) + " limite de credito: " + str(limite_de_credito))
			if total > limite_de_credito:
				title = "Límite de crédito excedido."
				message = """Se excedio el límite de crédito: \n
								Límite de credito: $""" + str(limite_de_credito.addComa()) + """\n
								Costo total: $""" + str(total.addComa()) + """
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

