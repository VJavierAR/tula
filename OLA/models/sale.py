from odoo import models, fields, api,_
import datetime, time
from odoo import exceptions
import logging, ast
_logger = logging.getLogger(__name__)
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

class sale(models.Model):
	_inherit = 'sale.order'

	bloqueo_limite_credito = fields.Boolean(
		string='Bloqueo por exceder límite de crédito',
		default=False,
		store=True
	)
	mensaje_limite_de_credito = fields.Text(
		string='Mensaje al exceder límite de crédito',
		store=True
	)
	limite_credito_actual = fields.Integer(
		string='Saldo disponible de límite de crédito',
		compute='_compute_limite_credito_actual'
	)
	limite_credito_conglomerado_actual = fields.Integer(
		string='Saldo disponible de límite de céredito de conglomerado',
		compute='_compute_limite_credito_conglomerado_actual'
	)


	productos_sugeridos = fields.One2many('product.suggested','rel_id')
	arreglo = fields.Char(default='[]')
	urgencia = fields.Selection(selection=[('Urgente','Urgente'),('Muy urgente','Muy urgente')], string="Urgencia")
	state = fields.Selection(
		[
			('draft', 'Quotation'),
			('sent', 'Quotation Sent'),
			('auto', 'Autorizar'),
			('sale', 'Sales Order'),
			('done', 'Locked'),
			('cancel', 'Cancelled'),
		], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')


	def action_confirm(self):
		check=self.mapped('order_line.bloqueo')
		if(True in check):
			self.write({'state':'auto'})
		if(True not in check):
			if self._get_forbidden_state_confirm() & set(self.mapped('state')):
				raise UserError(_(
			        'It is not allowed to confirm an order in the following states: %s'
			    ) % (', '.join(self._get_forbidden_state_confirm())))

			for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
				order.message_subscribe([order.partner_id.id])
			self.write({
			    'state': 'sale',
			    'date_order': fields.Datetime.now()
			})

			# Context key 'default_name' is sometimes propagated up to here.
			# We don't need it and it creates issues in the creation of linked records.
			context = self._context.copy()
			context.pop('default_name', None)

			self.with_context(context)._action_confirm()
			if self.env.user.has_group('sale.group_auto_done_setting'):
				self.action_done()
			_logger.info(self.company_id.auto_picking)
			if(self.company_id.auto_picking):
				for pi in self.picking_ids:
					precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
					no_quantities_done = all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in pi.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
					no_reserved_quantities = all(float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in pi.move_line_ids)
					pi.action_assign()
					_logger.info(pi._check_backorder() )
					if(pi._check_backorder()==False):
						pi.action_done()
			return True

	@api.onchange('arreglo')
	def addsegesst(self):
		if(self.arreglo!='[]'):
			data=eval(self.arreglo)
			dat=self.env['product.product'].browse(data)
			for d in dat:
				_logger.info(d.id)
				self.order_line.write({'product_id':d.id,'order_id':self.id,'product_uom_qty':1,'name':d.description,'price_unit':d.lst_price})

	@api.onchange('productos_sugeridos')
	def agregar(self):
		for sug in self.productos_sugeridos:
			if(sug.agregar==True and sug.bandera==1):
				self.order_line=[(0, 0, {'product_id':sug.product_sug.id})]

	@api.depends('partner_id')
	def _compute_limite_credito_actual(self):
		for rec in self:
			if rec.partner_id.id:
				limite_de_credito = rec.partner_id.limite_credito
				state_facturas_no_pagadas = ['draft', 'posted']
				facturas_no_pagadas = rec.env['account.move'].search(
					[
						("invoice_payment_state", "=", "not_paid"),
						("state", "in", state_facturas_no_pagadas),
						("partner_id", "=", rec.partner_id.id)
					]
				)
				total_de_facturas_no_pagadas = 0
				if facturas_no_pagadas:
					for factura_no_pagada in facturas_no_pagadas:
						total_de_facturas_no_pagadas += factura_no_pagada.amount_total
				rec['limite_credito_actual'] = limite_de_credito - total_de_facturas_no_pagadas
			else:
				rec['limite_credito_actual'] = 0

	@api.depends('partner_id')
	def _compute_limite_credito_conglomerado_actual(self):
		for rec in self:
			if rec.partner_id.id:
				limite_de_credito_conglomerado = rec.partner_id.limite_credito_conglomerado
				state_facturas_no_pagadas = ['draft', 'posted']
				facturas_no_pagadas = rec.env['account.move'].sudo().search(
					[
						("invoice_payment_state", "=", "not_paid"),
						("state", "in", state_facturas_no_pagadas),
						("partner_id", "=", rec.partner_id.id)
					]
				)
				total_de_facturas_no_pagadas = 0
				if facturas_no_pagadas:
					for factura_no_pagada in facturas_no_pagadas:
						total_de_facturas_no_pagadas += factura_no_pagada.amount_total
				rec['limite_credito_conglomerado_actual'] = limite_de_credito_conglomerado - total_de_facturas_no_pagadas
			else:
				rec['limite_credito_conglomerado_actual'] = 0

	@api.onchange('order_line', 'payment_term_id')
	def comprobar_limite_de_credito_company_unica(self):
		pago_de_contado_id = 1
		if len(self.order_line) > 0 and self.partner_id.id and self.payment_term_id.id and self.payment_term_id.id != pago_de_contado_id:
			total = self.amount_total
			limite_de_credito = self.partner_id.limite_credito
			limite_de_credito_conglomerado = self.partner_id.limite_credito_conglomerado

			state_facturas_no_pagadas = ['draft', 'posted']

			title = "Alertas: "
			message = """Mensajes: \n"""
			genero_alertas = False

			title_restriccion_dias_factura = ""
			message_factura = ""
			genero_alertas_facturas = False


			# Caso en que excede el limite de credito las facturas no pagadas y la linea de pedido de venta
			facturas_no_pagadas = self.env['account.move'].search(
				[
					("invoice_payment_state", "=", "not_paid"),
					("state", "in", state_facturas_no_pagadas),
					("partner_id", "=", self.partner_id.id)
				]
			)
			_logger.info("facturas_no_pagadas_limite_de_credito_unico: ")
			_logger.info(facturas_no_pagadas)
			total_de_facturas_no_pagadas = 0
			if facturas_no_pagadas:
				for factura_no_pagada in facturas_no_pagadas:
					total_de_facturas_no_pagadas += factura_no_pagada.amount_total

			total_con_facturas = total + total_de_facturas_no_pagadas
			_logger.info("total_con_facturas: " + str(total_con_facturas) + " > limite_de_credito:" + str(limite_de_credito))
			if total_con_facturas > limite_de_credito:
				title = title + "Límite de crédito excedido. | "
				message = message + """Se excedio el límite de crédito por facturas no pagadas y total del pedido de venta actual: \n
				Límite de credito: $""" + str(limite_de_credito) + """\n
				Costo total de pedido de venta actual: $""" + str(total) + """\n
				Costo total en facturas no pagadas: $""" + str(total_de_facturas_no_pagadas) + """\n
				Suma total: $""" + str(total_con_facturas) + """\n
				Facturas no pagadas: """ + str(facturas_no_pagadas.mapped('name')) + """\n
				""".rstrip() + "\n\n"
				genero_alertas = True

			#Caso en que excede el limite de credito de conglomerado las facturas no pagadas y la linea de pedido de venta
			facturas_no_pagadas_companies = self.env['account.move'].sudo().search(
				[
					("invoice_payment_state", "=", "not_paid"),
					("state", "in", state_facturas_no_pagadas),
					("partner_id", "=", self.partner_id.id)
				]
			)
			_logger.info("facturas_no_pagadas_companies: ")
			_logger.info(facturas_no_pagadas_companies)
			plazo_de_pago_cliente = self.partner_id.plazo_de_pago.line_ids.mapped('days')[-1]
			total_de_facturas_no_pagadas_companies = 0
			if facturas_no_pagadas_companies:
				title_restriccion_dias_factura = "Plazo de pago excedido en facturas. | "
				message_factura += """Existe una o más facturas no pagadas con un mayor número de días al plazo de pago del cliente:""".rstrip() + "\n"
				for factura_no_pagada in facturas_no_pagadas_companies:
					total_de_facturas_no_pagadas_companies += factura_no_pagada.amount_total
					fecha_de_creacion = str(factura_no_pagada.create_date).split(' ')[0]
					converted_date = datetime.datetime.strptime(fecha_de_creacion, '%Y-%m-%d').date()
					fecha_actual = datetime.date.today()
					dias_transcuridos = (fecha_actual - converted_date).days
					_logger.info("fecha_de_creacion: " + str(converted_date) + " fecha_actual: " + str(fecha_actual) + " dias_transcuridos: " + str(dias_transcuridos))
					if dias_transcuridos > plazo_de_pago_cliente:
						message_factura += """Factura no pagada: """ + str(factura_no_pagada.name) + """\n
						Fecha de creación de factura no pagada: """ + str(converted_date) + """\n
						Plazo de pago de cliente: """ + str(plazo_de_pago_cliente) + """\n
						Días de transcurridos de factura no pagada: """ + str(dias_transcuridos) + """\n """
						genero_alertas_facturas = True
				message_factura = message_factura + "".rstrip() + "\n"

			total_con_facturas_companies = total + total_de_facturas_no_pagadas_companies
			_logger.info(
				"total_con_facturas: " + str(total_con_facturas_companies) + " > limite_de_credito conglomerado:" + str(limite_de_credito_conglomerado))
			if total_con_facturas_companies > limite_de_credito_conglomerado:
				title = title + "Límite de crédito de conglomerado excedido. | "
				message = message + """Se excedio el límite de crédito de conglomerado por facturas no pagadas y total del pedido de venta actual: \n
				Límite de credito de conglomerado: $""" + str(limite_de_credito_conglomerado) + """\n
				Costo total de pedido de venta actual: $""" + str(total) + """\n
				Costo total en facturas no pagadas: $""" + str(total_de_facturas_no_pagadas_companies) + """\n
				Suma total: $""" + str(total_con_facturas_companies) + """\n
				Facturas no pagadas: """ + str(facturas_no_pagadas_companies.mapped('name')) + """\n
				""".rstrip() + "\n\n"
				genero_alertas = True

			usuarios_con_permisos = self.env['res.groups'].sudo().search(
				[
					("name", "=", "Confirma pedido de venta que excede límite de crédito")
				]
			).mapped('users')
			if usuarios_con_permisos:
				message += "El pedido de venta actual solo podrá ser validado por los siguientes usuarios: \n\n" + str(usuarios_con_permisos.mapped('name')) + " ".rstrip() + "\n\n"
			else:
				message += "El pedido de venta actual solo podrá ser validado por los usuarios que se encuentrán en el grupo \"Confirma pedido de venta que excede límite de crédito.\"".rstrip() + "\n\n"

			# Caso en que el plazo de pago excede el plazo de pago del cliente
			plazo_de_pago_cliente = self.partner_id.plazo_de_pago.line_ids.mapped('days')[-1]
			plazo_de_pago_sale = self.payment_term_id.line_ids.mapped('days')[-1]
			_logger.info("plazo_de_pago_cliente: " + str(plazo_de_pago_cliente) + " plazo_de_pago_sale: " +str(plazo_de_pago_sale))
			if plazo_de_pago_sale > plazo_de_pago_cliente:
				title = title + "Plazo de pago excedido. | "
				message = message + """Se excedio el plazo de pago del cliente: \n
				Plazo de pago de pedido de venta: """ + str(plazo_de_pago_sale) + """\n
				Plazo de pago de cliente: """ + str(plazo_de_pago_cliente) + """ """.rstrip() + "\n\n"
				genero_alertas = True

			# Caso en que genero alerta por facturas que exceden el plazo de pago
			if genero_alertas_facturas:
				title += title_restriccion_dias_factura
				message += message_factura
				genero_alertas = True

			if genero_alertas:
				self.bloqueo_limite_credito = True
				self.mensaje_limite_de_credito = message
				return {
					# 'value': {},
					'warning': {
						'title': title,
						'message': message
					}
				}

	def autorizar_sale_limite_de_credito(self):
		view = self.env.ref('OLA.sale_order_alerta_limite_credito_view')
		wiz = self.env['sale.order.alerta.limite.credito'].create(
			{
				'sale_id': self.id,
				'mensaje': self.mensaje_limite_de_credito
			}
		)
		return {
			'name': _('Autorizar excediendo límite de crédito'),
			'type': 'ir.actions.act_window',
			'view_mode': 'form',
			'res_model': 'sale.order.alerta.limite.credito',
			'views': [(view.id, 'form')],
			'view_id': view.id,
			'target': 'new',
			'res_id': wiz.id,
			'context': self.env.context,
		}

	#@api.onchange('order_line')
	def comprobar_limite_de_credito(self):
		check=self.mapped('order_line.bloqueo')
		if(True not in check):
			self.state='draft'
		if len(self.order_line) > 0 and self.partner_id:
			total = self.amount_total
			limite_de_credito = self.partner_id.limite_credito
			limite_de_credito_sucursal = self.partner_shipping_id.limite_credito_sucursal
			sucursal_nombre = self.partner_shipping_id.name

			sale_order_state_activos = ['draft', 'sent']
			genero_alertas = False
			title = "Alertas: "
			message = """Mensajes: \n"""
			_logger.info("total: " + str(total) + " limite de credito: " + str(
				limite_de_credito) + " limite de credito por sucursal: " + str(limite_de_credito_sucursal))

			# Caso en que excede limite de credito la linea de pediodo de venta
			if total > limite_de_credito:
				title = title + "Límite de crédito excedido. | "
				message = message + """Se excedio el límite de crédito: \n
					Límite de credito: $""" + str(limite_de_credito) + """\n
					Costo total: $""" + str(total) + """\n
					""".rstrip() + "\n\n"
				genero_alertas = True

			# Caso en que excede límite de crédito por sucursal la línea de pedido de venta
			if total > limite_de_credito_sucursal:
				title = title + "Límite de crédito de sucursal excedido. | "
				message = message + """Se excedio el límite de crédito de la sucursal \"""" + sucursal_nombre + """\": \n
					Límite de credito de sucursal: $""" + str(limite_de_credito_sucursal) + """\n
					Costo total: $""" + str(total) + """\n
					""".rstrip() + "\n\n"
				genero_alertas = True

			# Caso en que excede limite de credito con la suma de las ventas activas.
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

				# Caso en que excede limite de credito por sucursal con la suma de las ventas activas.
				ventas_activas_sucursal = self.sudo().env['sale.order'].search(
					[
						('partner_shipping_id', '=', self.partner_shipping_id.id),
						('id', '!=', self._origin.id),
						('state', 'in', sale_order_state_activos)
					]
				).mapped('amount_total')
				_logger.info("ventas_activas_sucursal.amount_total: " + str(ventas_activas_sucursal))
				if ventas_activas_sucursal:
					total_de_ventas_activas_sucursal = 0
					for venta in ventas_activas_sucursal:
						total_de_ventas_activas_sucursal += venta
					total_de_ventas_activas_sucursal += total
					_logger.info('total_de_ventas_activas_sucursal: ' + str(total_de_ventas_activas_sucursal))

					if total_de_ventas_activas_sucursal > limite_de_credito_sucursal:
						title = title + "Límite de crédito de sucursal excedido en ventas. | "
						message = message + """Se excedio el límite de crédito de la sucursal \"""" + sucursal_nombre + """\" por total de todos los pedido de venta activos: \n
							Límite de credito de sucursal: $""" + str(limite_de_credito_sucursal) + """\n
							Costo total de todos los pedido de venta activos: $""" + str(
							total_de_ventas_activas_sucursal) + """
							""".rstrip() + "\n\n"
						genero_alertas = True

				# Caso en que excede el limite de credito las facturas no pagadas y la linea de pedido de venta
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
							""".rstrip() + "\n\n"
						genero_alertas = True

				# Caso en que excede el limite de credito por sucursal las facturas no pagadas y la linea de pedido de venta
				facturas_no_pagadas_sucursal = self.sudo().env['account.move'].search(
					["&", "&",
					 ["invoice_payment_state", "=", "not_paid"],
					 ["state", "=", "posted"],
					 ["partner_shipping_id", "=", self.partner_shipping_id.id]
					 ]
				)
				_logger.info("facturas_no_pagadas_sucursal: ")
				_logger.info(facturas_no_pagadas_sucursal)
				if facturas_no_pagadas_sucursal:
					total_de_facturas_no_pagadas_sucursal = 0
					for factura_no_pagada in facturas_no_pagadas_sucursal:
						total_de_facturas_no_pagadas = total_de_facturas_no_pagadas_sucursal + factura_no_pagada.amount_total
					total_con_facturas = total + total_de_facturas_no_pagadas_sucursal

					if total_con_facturas > limite_de_credito_sucursal:
						title = title + "Límite de crédito excedido. | "
						message = message + """Se excedio el límite de crédito de la sucursal \"""" + sucursal_nombre + """\" por facturas no pagadas y total del pedido de venta actual: \n
							Límite de credito de sucursal: $""" + str(limite_de_credito_sucursal) + """\n
							Costo total de pedido de venta actual: $""" + str(total) + """
							Costo total en facturas no pagadas de sucursal: $""" + str(
							total_de_facturas_no_pagadas_sucursal) + """\n\n
							Facturas no pagadas de sucursal: """ + str(facturas_no_pagadas_sucursal.mapped('name')) + """\n
							""".rstrip() + "\n\n"
						genero_alertas = True

				if genero_alertas:
					return {
						# 'value': {},
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
	    return result

	# def write(self, vals):
	# 	check=self.mapped('order_line.bloqueo')
	# 	em=self.company_id
	# 	if(True not in check):
	# 		self.state='draft'
	# 		if(em.auto_picking):
	# 			self.action_confirm()
	# 		if(em.auto_picking==False):
	# 			result = super(sale, self).write(vals)
	# 	if(True in check):
	# 		self.state='auto'
	# 		result = super(sale, self).write(vals)
	# 	return result


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
