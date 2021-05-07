from odoo import models, fields, api,_
import datetime, time
import logging, ast
from odoo.exceptions import UserError,AccessDenied,Warning
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
	partner_id = fields.Many2one(
		comodel_name='res.partner',
		ondelete='restrict',
		string='Cliente',
		store=True,
		copy=True,
		required=False,
		track_visibility='onchange'
	)
	partner_invoice_id = fields.Many2one(
		comodel_name='res.partner',
		ondelete='restrict',
		string='Dirección de factura',
		store=True,
		copy=True,
		required=False,
		#track_visibility='onchange'
	)
	partner_shipping_id = fields.Many2one(
		comodel_name='res.partner',
		ondelete='restrict',
		string='Dirección de entrega',
		store=True,
		copy=True,
		required=False,
		#track_visibility='onchange'
	)
	pricelist_id = fields.Many2one(
		comodel_name='product.pricelist',
		ondelete='restrict',
		string='Tarifa',
		store=True,
		copy=True,
		required=False,
		#track_visibility='onchange'
	)
	arreglo2=fields.Char()
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

	def conf(self):
		check = self.mapped('order_line.bloqueo')
		U = self.env['res.groups'].sudo().search([("name", "=", "Confirma pedido de venta que excede límite de crédito")]).mapped('users.id')
		m = self.env['res.groups'].sudo().search([("name", "=", "Confirma pedido de venta que excede límite de crédito")]).mapped('users.email')
		if True in check:
			self.write({'state':'auto'})
			template_id2=self.env.ref('OLA.notify_descuento_email_template')
			#template_id2=self.env['mail.template'].search([('id','=',41)], limit=1)
			mail=template_id2.generate_email(self.id)
			#dest=''
			#for mi in m:
			#	dest=dest+str(mi)+','
			mail['email_to']=str(m).replace('[','').replace(']','')
			self.env['mail.mail'].create(mail).send()
		if True not in check or self.env.user.id in U:
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
			return True

	def action_confirm(self):
		self.conf()
		if self.company_id.auto_picking:
			_logger.info(self.picking_ids.mapped('state'))
			for pi in self.picking_ids:
				if pi.state == 'assigned':
					pi.action_confirm()
					pi.move_lines._action_assign()
					pi.action_assign()
					_logger.info(self.picking_ids.mapped('move_line_ids.state'))
					#pi.move_lines._action_assign()
					#pi.move_lines._action_done()
					return pi.button_validate()
					#pi._autoconfirm_picking()
				if pi.state in ('waiting','confirmed'):
					raise Warning(_('No hay stock para el pedido'))
					#_logger.info(self.picking_ids.mapped('move_line_ids.state'))
					#return {'warning': {'title': 'Sin stock','message': 'No hay stock'}}


						

	@api.onchange('productos_sugeridos')
	def agregarci(self):
		for sug in self.productos_sugeridos:
			if(sug.agregar==True):
				if(sug.product_sug.id not in self.order_line.mapped('product_id.id')):
					pro=dict()
					pro['product_id']=sug.product_sug.id
					pro['order_id']=self.id
					pro['product_uom_qty']=sug.product_sug.uom_id.id
					pro['name']=sug.product_sug.description
					pro['price_unit']=sug.product_sug.lst_price
					self.order_line=[(0, 0,pro)]
					for o in self.order_line:
						o.buscaProductos()

	@api.depends('partner_id')
	def _compute_limite_credito_actual(self):
		for rec in self:
			if rec.partner_id.id:
				limite_de_credito = rec.partner_id.limite_credito
				state_facturas_no_pagadas = ['posted']
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
				state_facturas_no_pagadas = ['posted']
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

		if not self.payment_term_id.id and self.limite_credito_actual == 0:
			title = "Alertas: "
			message = """Mensajes: \n"""
			genero_alertas = False

			title = title + "Límite de crédito excedido. | "
			message = message + """Se excedio el límite de crédito del cliente: \n
					Límite de crédito: """ + str(self.limite_credito_actual) + """\n
					Plazo de pago de pedido de venta: No definido """.rstrip() + "\n\n"
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

		if len(self.order_line) > 0 and self.partner_id.id and self.payment_term_id.id != pago_de_contado_id:
			total = self.amount_total
			limite_de_credito = self.partner_id.limite_credito
			limite_de_credito_conglomerado = self.partner_id.limite_credito_conglomerado

			state_facturas_no_pagadas = ['posted']
			colchon_de_credito = self.partner_id.colchon_credito
			title = "Alertas: "
			message = """Mensajes: \n"""
			genero_alertas = False
			genero_alerta_limite = False
			genero_alerta_limite_conglomerado = False
			genero_alerta_plazo = False

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
			total_de_facturas_no_pagadas = 0
			if facturas_no_pagadas:
				for factura_no_pagada in facturas_no_pagadas:
					total_de_facturas_no_pagadas += factura_no_pagada.amount_total

			total_con_facturas = total + total_de_facturas_no_pagadas
			if total_con_facturas > limite_de_credito:
				title = title + "Límite de crédito excedido. | "
				message = message + """Se excedio el límite de crédito por facturas no pagadas y total del pedido de venta actual: \n
						Límite de credito: $""" + str(limite_de_credito) + """\n
						Costo total de pedido de venta actual: $""" + str(total) + """\n
						Costo total en facturas no pagadas: $""" + str(total_de_facturas_no_pagadas) + """\n
						Suma total: $""" + str(total_con_facturas) + """\n
						Facturas no pagadas: """ + str(facturas_no_pagadas.mapped('name')) + """\n
						""".rstrip() + "\n\n"
				genero_alerta_limite = True
			else:
				genero_alerta_limite = False

			# Caso en que excede el limite de credito de conglomerado las facturas no pagadas y la linea de pedido de venta
			facturas_no_pagadas_companies = self.env['account.move'].sudo().search(
				[
					("invoice_payment_state", "=", "not_paid"),
					("state", "in", state_facturas_no_pagadas),
					("partner_id", "=", self.partner_id.id)
				]
			)

			plazo_de_pago_cliente = 0
			if self.partner_id.property_payment_term_id.id and self.partner_id.property_payment_term_id.line_ids.mapped('days'):
				plazo_de_pago_cliente = self.partner_id.property_payment_term_id.line_ids.mapped('days')[
										-1] + colchon_de_credito
			# plazo_de_pago_cliente = self.partner_id.property_payment_id.line_ids.mapped('days')[-1]
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
					#_logger.info("fecha_de_creacion: " + str(converted_date) + " fecha_actual: " + str(
					#	fecha_actual) + " dias_transcuridos: " + str(dias_transcuridos))
					if dias_transcuridos > plazo_de_pago_cliente:
						message_factura += """Factura no pagada: """ + str(factura_no_pagada.name) + """\n
								Fecha de creación de factura no pagada: """ + str(converted_date) + """\n
								Plazo de pago de cliente: """ + str(plazo_de_pago_cliente) + """\n
								Días de transcurridos de factura no pagada: """ + str(dias_transcuridos) + """\n """
						genero_alertas_facturas = True
				message_factura = message_factura + "".rstrip() + "\n"

			total_con_facturas_companies = total + total_de_facturas_no_pagadas_companies
			if total_con_facturas_companies > limite_de_credito_conglomerado:
				title = title + "Límite de crédito de conglomerado excedido. | "
				message = message + """Se excedio el límite de crédito de conglomerado por facturas no pagadas y total del pedido de venta actual: \n
						Límite de credito de conglomerado: $""" + str(limite_de_credito_conglomerado) + """\n
						Costo total de pedido de venta actual: $""" + str(total) + """\n
						Costo total en facturas no pagadas: $""" + str(total_de_facturas_no_pagadas_companies) + """\n
						Suma total: $""" + str(total_con_facturas_companies) + """\n
						Facturas no pagadas: """ + str(facturas_no_pagadas_companies.mapped('name')) + """\n
						""".rstrip() + "\n\n"
				genero_alerta_limite_conglomerado = True
			else:
				genero_alerta_limite_conglomerado = False

			usuarios_con_permisos = self.env['res.groups'].sudo().search(
				[
					("name", "=", "Confirma pedido de venta que excede límite de crédito")
				]
			).mapped('users')
			if usuarios_con_permisos:
				message += "El pedido de venta actual solo podrá ser validado por los siguientes usuarios: \n\n" + str(
					usuarios_con_permisos.mapped('name')) + " ".rstrip() + "\n\n"
			else:
				message += "El pedido de venta actual solo podrá ser validado por los usuarios que se encuentrán en el grupo \"Confirma pedido de venta que excede límite de crédito.\"".rstrip() + "\n\n"

			# Caso en que el plazo de pago excede el plazo de pago del cliente
			plazo_de_pago_cliente = -1
			if self.partner_id.property_payment_term_id.id and self.partner_id.property_payment_term_id.line_ids.mapped('days'):
				plazo_de_pago_cliente = self.partner_id.property_payment_term_id.line_ids.mapped('days')[
											-1] + colchon_de_credito
			plazo_de_pago_sale = -1
			if self.payment_term_id.id and self.payment_term_id.line_ids.mapped('days'):
				plazo_de_pago_sale = self.payment_term_id.line_ids.mapped('days')[-1]
			if plazo_de_pago_sale == -1 or plazo_de_pago_cliente == -1:
				title = title + "Plazo de pago no definido. | "
				message = message + """No se definio un plazo de pago:"""
				if plazo_de_pago_sale == -1:
					message += """\nPlazo de pago de pedido de venta: No definido"""
				if plazo_de_pago_cliente == -1:
					message += """\nPlazo de pago de cliente: No definido"""
				message = message + " ".rstrip() + "\n\n"
				genero_alerta_plazo = True
			else:
				if plazo_de_pago_sale > plazo_de_pago_cliente:
					title = title + "Plazo de pago excedido. | "
					message = message + """Se excedio el plazo de pago del cliente: \n
							Plazo de pago de pedido de venta: """ + str(plazo_de_pago_sale) + """\n
							Plazo de pago de cliente: """ + str(plazo_de_pago_cliente) + """ """.rstrip() + "\n\n"
					genero_alerta_plazo = True
				else:
					genero_alerta_plazo = False

			# Caso en que genero alerta por facturas que exceden el plazo de pago
			if genero_alertas_facturas:
				title += title_restriccion_dias_factura
				message += message_factura

			if genero_alerta_limite or genero_alerta_limite_conglomerado or genero_alerta_plazo or genero_alertas_facturas:
				self.bloqueo_limite_credito = True
				self.mensaje_limite_de_credito = message
				return {
					# 'value': {},
					'warning': {
						'title': title,
						'message': message
					}
				}
			else:
				self.bloqueo_limite_credito = False
				self.mensaje_limite_de_credito = ""

		elif self.partner_id.id and self.payment_term_id.id and self.payment_term_id.id != pago_de_contado_id:
			title = "Alertas: "
			message = """Mensajes: \n"""
			genero_alertas = False

			# Caso en que el plazo de pago excede el plazo de pago del cliente
			plazo_de_pago_cliente = self.partner_id.property_payment_term_id.line_ids.mapped('days')[-1]
			plazo_de_pago_sale = self.payment_term_id.line_ids.mapped('days')[-1]
			#_logger.info("plazo_de_pago_cliente: " + str(plazo_de_pago_cliente) + " plazo_de_pago_sale: " + str(
			#	plazo_de_pago_sale))
			if plazo_de_pago_sale > plazo_de_pago_cliente:
				title = title + "Plazo de pago excedido. | "
				message = message + """Se excedio el plazo de pago del cliente: \n
									Plazo de pago de pedido de venta: """ + str(plazo_de_pago_sale) + """\n
									Plazo de pago de cliente: """ + str(
					plazo_de_pago_cliente) + """ """.rstrip() + "\n\n"
				genero_alertas = True
			else:
				self.bloqueo_limite_credito = False
				self.mensaje_limite_de_credito = ""
				genero_alertas = False

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
		elif self.payment_term_id.id and self.payment_term_id.id == pago_de_contado_id:
			self.bloqueo_limite_credito = False
			self.mensaje_limite_de_credito = ""

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

	def write(self, vals):
		check = self.mapped('order_line.bloqueo')
		em = self.company_id
		if True in check:
			vals['state']='draft'
		result = super(sale, self).write(vals)
		return result
		
	@api.onchange('order_line')
	def test(self):
		l=len(self.order_line)
		if(l>0):
			m=self.productos_sugeridos.mapped('product_sug.id')
			#self.productos_sugeridos=[(5,0,0)]
			arr=[]
			for p in self.order_line:
				pro={}
				ps=p.product_id.mapped('sug_rel.id')+p.product_id.product_tmpl_id.mapped('sug_rel.id')
				for pss in ps:
					if(pss not in m):
						pro['product_rel']=p.product_id.id
						pro['product_sug']=pss
						self.productos_sugeridos=[(0, 0, pro)]

class productSuggested(models.Model):
	_name='product.suggested'
	_description='Productos sugeridos'
	product_rel=fields.Many2one('product.product')
	product_sug=fields.Many2one('product.product')
	rel_id=fields.Many2one('sale.order')
	agregar=fields.Boolean()
