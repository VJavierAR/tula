from odoo import models, fields, api,_
import datetime, time
from odoo import exceptions
import logging, ast
_logger = logging.getLogger(__name__)

class sale(models.Model):
	_inherit = 'sale.order'

	productos_sugeridos = fields.One2many('product.suggested','rel_id')
	arreglo = fields.Char(default='[]')
	urgencia = fields.Selection(selection=[('Urgente','Urgente'),('Muy urgente','Muy urgente')], string="Urgencia")


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

			#Caso en que excede limite de credito la linea de pediodo de venta
			if total > limite_de_credito:
				title = title + "Límite de crédito excedido. | "
				message = message + """Se excedio el límite de crédito: \n
				Límite de credito: $""" + str(limite_de_credito) + """\n
				Costo total: $""" + str(total) + """\n
				""".rstrip() + "\n\n"
				genero_alertas = True

			#Caso en que excede limite de credito con la suma de las ventas activas.
			sale_order_state_activos = ['draft', 'sent']
			ventas_activas = self.sudo().env['sale.order'].search(
				[
					('partner_id', '=', self.partner_id.id),
					('id', '!=', self._origin.id),
					('state', 'in', sale_order_state_activos)
				]
			).mapped('amount_total')
			_logger.info("ventas_activas.amount_total: " + str(ventas_activas))
			if ventas_activas:
				total_de_ventas_activas = 0
				for venta in ventas_activas:
					total_de_ventas_activas += venta
				total_de_ventas_activas += total
				_logger.info('total_de_ventas_activas: ' + str(total_de_ventas_activas))
				if total_de_ventas_activas > limite_de_credito:
					title = title + "Límite de crédito excedido en ventas. | "
					message = message + """Se excedio el límite de crédito por total de todos los pedido de venta activos: \n
					Límite de credito: $""" + str(limite_de_credito) + """\n
					Costo total de todos los pedido de venta activos: $""" + str(total_de_ventas_activas) + """
					""".rstrip() + "\n\n"
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
					Costo total en facturas no pagadas: $""" + str(total_de_facturas_no_pagadas) + """\n\n
					Facturas no pagadas: """ + str(facturas_no_pagadas.mapped('name')) + """\n
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
	@api.model
	def create(self, vals):
	    if vals.get('name', _('New')) == _('New'):
	        seq_date = None
	        if 'date_order' in vals:
	            seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
	        if 'company_id' in vals:
	            vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
	                'sale.order', sequence_date=seq_date) or _('New')
	        else:
	            vals['name'] = self.env['ir.sequence'].next_by_code('sale.order', sequence_date=seq_date) or _('New')

	    # Makes sure partner_invoice_id', 'partner_shipping_id' and 'pricelist_id' are defined
	    if any(f not in vals for f in ['partner_invoice_id', 'partner_shipping_id', 'pricelist_id']):
	        partner = self.env['res.partner'].browse(vals.get('partner_id'))
	        addr = partner.address_get(['delivery', 'invoice'])
	        vals['partner_invoice_id'] = vals.setdefault('partner_invoice_id', addr['invoice'])
	        vals['partner_shipping_id'] = vals.setdefault('partner_shipping_id', addr['delivery'])
	        vals['pricelist_id'] = vals.setdefault('pricelist_id', partner.property_product_pricelist and partner.property_product_pricelist.id)
	    result = super(sale, self).create(vals)
	    _logger.info(vals['company_id'])
	    em=self.env['res.company'].browse(vals['company_id'])
	    _logger.info(em.auto_picking)
	    if(em.auto_picking):
	    	result.action_confirm()
	    return result


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

	x_studio_field_Ml1CB = fields.Float("Precio minímo", related="product_id.standard_price")

	@api.onchange('price_unit', 'discount')
	def precio_minimo(self):
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
