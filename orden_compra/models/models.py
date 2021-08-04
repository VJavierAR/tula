# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging, ast
_logger = logging.getLogger(__name__)


class Factura(models.Model):
	_inherit='account.move'
	almacen=fields.Many2one('stock.warehouse')
	orden_compra=fields.Many2one('purchase.order')

	def action_post(self):
		if self.filtered(lambda x: x.journal_id.post_at == 'bank_rec').mapped('line_ids.payment_id').filtered(lambda x: x.state != 'reconciled'):
			raise UserError(_("A payment journal entry generated in a journal configured to post entries only when payments are reconciled with a bank statement cannot be manually posted. Those will be posted automatically after performing the bank reconciliation."))
		if self.env.context.get('default_type'):
			context = dict(self.env.context)
			tipo=context['default_type']
			if(tipo=='in_invoice' and self.company_id.orden_compra):
				orden=self.env['purchase.order'].create({'partner_id':self.partner_id.id,'picking_type_id':self.almacen.in_type_id.id})
				for inv in self.invoice_line_ids:
					prod=dict()
					prod['product_id']=inv.product_id.id
					prod['product_qty']=inv.quantity
					prod['name']=inv.name
					prod['price_unit']=inv.price_unit
					prod['taxes_id']=inv.tax_ids.mapped('id')
					prod['order_id']=orden.id
					prod['product_uom']=inv.product_uom_id.id
					prod['date_planned']=inv.date
					p=self.env['purchase.order.line'].create(prod)
					p.write({'invoice_lines':[(6,0,inv.mapped('id'))]})
				orden.write({'invoice_ids':[(6,0,self.mapped('id'))]})
				self.write({'purchase_id':orden.id,'invoice_origin':orden.name,'orden_compra':orden.id})
				orden._compute_invoice()
			del context['default_type']
			self = self.with_context(context)
			self.post()
			return orden.boton_confirmar()

	def button_draft(self):
		AccountMoveLine = self.env['account.move.line']
		excluded_move_ids = []

		if self._context.get('suspense_moves_mode'):
			excluded_move_ids = AccountMoveLine.search(AccountMoveLine._get_suspense_moves_domain() + [('move_id', 'in', self.ids)]).mapped('move_id').ids
		for move in self:
			if move in move.line_ids.mapped('full_reconcile_id.exchange_move_id'):
			    raise UserError(_('You cannot reset to draft an exchange difference journal entry.'))
			if move.tax_cash_basis_rec_id:
			    raise UserError(_('You cannot reset to draft a tax cash basis journal entry.'))
			if move.restrict_mode_hash_table and move.state == 'posted' and move.id not in excluded_move_ids:
			    raise UserError(_('You cannot modify a posted entry of this journal because it is in strict mode.'))
			# We remove all the analytics entries for this journal
			move.mapped('line_ids.analytic_line_ids').unlink()
		self.mapped('line_ids').remove_move_reconcile()
		self.write({'state': 'draft'})
		tipo=self.type
		if(tipo=='in_invoice' and self.company_id.orden_compra):
			if(self.orden_compra.mapped('id')!=[]):
				self.write({'invoice_origin':''})
				for pi in self.orden_compra.picking_ids:
					pi.unlink()
				self.orden_compra.write({'state': 'cancel'})
				self.orden_compra.unlink()

class LinesFactura(models.Model):
	_inherit='account.move.line'
	costo=fields.Float(related='product_id.standard_price',store=True)
	precio=fields.Float(related='product_id.lst_price',store=True)
	ultimo_provedor=fields.Many2one('res.partner',store=True,compute='ultimoProvedor')
	ultimo_precio_compra=fields.Float(store=True)
	stock_total=fields.Float(store=True)
	stock_quant=fields.Many2many('stock.quant',store=True)
	nueva_utilidad=fields.Float(store=True)
	utilida=fields.Float(related='product_id.x_studio_utilidad_precio_de_venta',store=True)
	nuevo_costo=fields.Float(store=True)
	nuevo_precio=fields.Float(store=True)

	@api.depends('product_id','price_unit','quantity','nuevo_precio','nueva_utilidad')
	def ultimoProvedor(self):
		for record in self:
			_logger.info(record.product_id.id!=False)
			if(record.product_id.id!=False):
				ultimo=self.env['purchase.order.line'].search([['product_id','=',record.product_id.id]],order='date_planned desc',limit=1)
				record['ultimo_provedor']=ultimo.order_id.partner_id.id
				record['ultimo_precio_compra']=ultimo.price_unit
				wa=self.env['stock.warehouse'].search([['stock_visible','=',True]])
				quant=self.env['stock.quant'].search([['location_id','in',wa.mapped('lot_stock_id.id')],['product_id','=',record.product_id.id]])
				record['stock_quant']=[(5,0,0)]
				record['stock_quant']=[(6,0,quant.mapped('id'))]
				record['stock_total']=sum(quant.mapped('quantity'))
				cost=self.env['stock.valuation.layer'].search([['product_id','=',record.product_id.id]])
				#utilida=((record.precio-cost)/record.precio)*100
				#record['utilida']=utilida
				unidades=sum(cost.mapped('quantity'))+record.quantity
				costos=sum(cost.mapped('value'))+record.price_unit
				new_cost=costos/unidades if(unidades>0) else 0
				record['nuevo_costo']=new_cost
				nuevautil=record.utilida if(record.nueva_utilidad==0) else record.nueva_utilidad
				precio=record.precio if(record.nuevo_precio==0) else record.nuevo_precio
				record['nuevo_precio']=(record.costo * nuevautil / 100) + record.costo
				record['nueva_utilidad']=((record.precio-new_cost)/precio)*100


#	@api.onchange('nueva_utilidad')
#	def nuevaUtil(self):
#		for record in self:
#			if(record.product_id.id):
#				if(record.nuevo_precio!=0):
#					if(record.nueva_utilidad!=0):
	@api.model_create_multi
	def create(self, vals_list):
		# OVERRIDE
		ACCOUNTING_FIELDS = ('debit', 'credit', 'amount_currency')
		BUSINESS_FIELDS = ('price_unit', 'quantity', 'discount', 'tax_ids')

		for vals in vals_list:
			move = self.env['account.move'].browse(vals['move_id'])
			vals.setdefault('company_currency_id', move.company_id.currency_id.id) # important to bypass the ORM limitation where monetary fields are not rounded; more info in the commit message
			if('nuevo_precio' in vals or 'nueva_utilidad' in vals):
				product=self.env['product.product'].browse(vals['product_id'])
				product.write({'x_studio_utilidad_precio_de_venta':vals['nueva_utilidad']})
			if move.is_invoice(include_receipts=True):
				currency = move.currency_id
				partner = self.env['res.partner'].browse(vals.get('partner_id'))
				taxes = self.resolve_2many_commands('tax_ids', vals.get('tax_ids', []), fields=['id'])
				tax_ids = set(tax['id'] for tax in taxes)
				taxes = self.env['account.tax'].browse(tax_ids)

				# Ensure consistency between accounting & business fields.
				# As we can't express such synchronization as computed fields without cycling, we need to do it both
				# in onchange and in create/write. So, if something changed in accounting [resp. business] fields,
				# business [resp. accounting] fields are recomputed.
				if any(vals.get(field) for field in ACCOUNTING_FIELDS):
					if vals.get('currency_id'):
						balance = vals.get('amount_currency', 0.0)
					else:
						balance = vals.get('debit', 0.0) - vals.get('credit', 0.0)
						price_subtotal = self._get_price_total_and_subtotal_model(
						    vals.get('price_unit', 0.0),
						    vals.get('quantity', 0.0),
						    vals.get('discount', 0.0),
						    currency,
						    self.env['product.product'].browse(vals.get('product_id')),
						    partner,
						    taxes,
						    move.type,
						).get('price_subtotal', 0.0)
						vals.update(self._get_fields_onchange_balance_model(
						    vals.get('quantity', 0.0),
						    vals.get('discount', 0.0),
						    balance,
						    move.type,
						    currency,
						    taxes,
						    price_subtotal
						))
						vals.update(self._get_price_total_and_subtotal_model(
						    vals.get('price_unit', 0.0),
						    vals.get('quantity', 0.0),
						    vals.get('discount', 0.0),
						    currency,
						    self.env['product.product'].browse(vals.get('product_id')),
						    partner,
						    taxes,
						    move.type,
						))
				elif any(vals.get(field) for field in BUSINESS_FIELDS):
					vals.update(self._get_price_total_and_subtotal_model(
					    vals.get('price_unit', 0.0),
					    vals.get('quantity', 0.0),
					    vals.get('discount', 0.0),
					    currency,
					    self.env['product.product'].browse(vals.get('product_id')),
					    partner,
					    taxes,
					    move.type,
					))
					vals.update(self._get_fields_onchange_subtotal_model(
					    vals['price_subtotal'],
					    move.type,
					    currency,
					    move.company_id,
					    move.date,
					))

		lines = super(AccountMoveLine, self).create(vals_list)

		moves = lines.mapped('move_id')
		if self._context.get('check_move_validity', True):
		    moves._check_balanced()
		moves._check_fiscalyear_lock_date()
		lines._check_tax_lock_date()

		return lines

	def write(self, vals):
		# OVERRIDE
		def field_will_change(line, field_name):
			if field_name not in vals:
				return False
			field = line._fields[field_name]
			if field.type == 'many2one':
				return line[field_name].id != vals[field_name]
			if field.type in ('one2many', 'many2many'):
				current_ids = set(line[field_name].ids)
				after_write_ids = set(r['id'] for r in line.resolve_2many_commands(field_name, vals[field_name], fields=['id']))
				return current_ids != after_write_ids
			if field.type == 'monetary' and line[field.currency_field]:
				return not line[field.currency_field].is_zero(line[field_name] - vals[field_name])
			return line[field_name] != vals[field_name]

		ACCOUNTING_FIELDS = ('debit', 'credit', 'amount_currency')
		BUSINESS_FIELDS = ('price_unit', 'quantity', 'discount', 'tax_ids')
		PROTECTED_FIELDS_TAX_LOCK_DATE = ['debit', 'credit', 'tax_line_id', 'tax_ids', 'tag_ids']
		PROTECTED_FIELDS_LOCK_DATE = PROTECTED_FIELDS_TAX_LOCK_DATE + ['account_id', 'journal_id', 'amount_currency', 'currency_id', 'partner_id']
		PROTECTED_FIELDS_RECONCILIATION = ('account_id', 'date', 'debit', 'credit', 'amount_currency', 'currency_id')

		account_to_write = self.env['account.account'].browse(vals['account_id']) if 'account_id' in vals else None

		# Check writing a deprecated account.
		if account_to_write and account_to_write.deprecated:
			raise UserError(_('You cannot use a deprecated account.'))
		if('nuevo_precio' in vals or 'nueva_utilidad' in vals):
			product=self.env['product.product'].browse(vals['product_id'])
			product.write({'x_studio_utilidad_precio_de_venta':vals['nueva_utilidad']})
		# when making a reconciliation on an existing liquidity journal item, mark the payment as reconciled
		for line in self:
			if line.parent_state == 'posted':
				if line.move_id.restrict_mode_hash_table and set(vals).intersection(INTEGRITY_HASH_LINE_FIELDS):
					raise UserError(_("You cannot edit the following fields due to restrict mode being activated on the journal: %s.") % ', '.join(INTEGRITY_HASH_LINE_FIELDS))
				if any(key in vals for key in ('tax_ids', 'tax_line_ids')):
					raise UserError(_('You cannot modify the taxes related to a posted journal item, you should reset the journal entry to draft to do so.'))
			if 'statement_line_id' in vals and line.payment_id:
				# In case of an internal transfer, there are 2 liquidity move lines to match with a bank statement
				if all(line.statement_id for line in line.payment_id.move_line_ids.filtered(
				        lambda r: r.id != line.id and r.account_id.internal_type == 'liquidity')):
					line.payment_id.state = 'reconciled'

			# Check the lock date.
			if any(self.env['account.move']._field_will_change(line, vals, field_name) for field_name in PROTECTED_FIELDS_LOCK_DATE):
				line.move_id._check_fiscalyear_lock_date()

			# Check the tax lock date.
			if any(self.env['account.move']._field_will_change(line, vals, field_name) for field_name in PROTECTED_FIELDS_TAX_LOCK_DATE):
				line._check_tax_lock_date()

			# Check the reconciliation.
			if any(self.env['account.move']._field_will_change(line, vals, field_name) for field_name in PROTECTED_FIELDS_RECONCILIATION):
				line._check_reconciliation()

			# Check switching receivable / payable accounts.
			if account_to_write:
				account_type = line.account_id.user_type_id.type
				if line.move_id.is_sale_document(include_receipts=True):
					if (account_type == 'receivable' and account_to_write.user_type_id.type != account_type) \
				            or (account_type != 'receivable' and account_to_write.user_type_id.type == 'receivable'):
						raise UserError(_("You can only set an account having the receivable type on payment terms lines for customer invoice."))
				if line.move_id.is_purchase_document(include_receipts=True):
					if (account_type == 'payable' and account_to_write.user_type_id.type != account_type) \
				            or (account_type != 'payable' and account_to_write.user_type_id.type == 'payable'):
						raise UserError(_("You can only set an account having the payable type on payment terms lines for vendor bill."))

		result = True
		for line in self:
			cleaned_vals = line.move_id._cleanup_write_orm_values(line, vals)
			if not cleaned_vals:
				continue

			result |= super(AccountMoveLine, line).write(cleaned_vals)

			if not line.move_id.is_invoice(include_receipts=True):
				continue

			# Ensure consistency between accounting & business fields.
			# As we can't express such synchronization as computed fields without cycling, we need to do it both
			# in onchange and in create/write. So, if something changed in accounting [resp. business] fields,
			# business [resp. accounting] fields are recomputed.
			if any(field in cleaned_vals for field in ACCOUNTING_FIELDS):
				balance = line.currency_id and line.amount_currency or line.debit - line.credit
				price_subtotal = line._get_price_total_and_subtotal().get('price_subtotal', 0.0)
				to_write = line._get_fields_onchange_balance(
				    balance=balance,
				    price_subtotal=price_subtotal,
				)
				to_write.update(line._get_price_total_and_subtotal(
				    price_unit=to_write.get('price_unit', line.price_unit),
				    quantity=to_write.get('quantity', line.quantity),
				    discount=to_write.get('discount', line.discount),
				))
				result |= super(AccountMoveLine, line).write(to_write)
			elif any(field in cleaned_vals for field in BUSINESS_FIELDS):
				to_write = line._get_price_total_and_subtotal()
				to_write.update(line._get_fields_onchange_subtotal(
				    price_subtotal=to_write['price_subtotal'],
				))
				result |= super(AccountMoveLine, line).write(to_write)

			# Check total_debit == total_credit in the related moves.
			if self._context.get('check_move_validity', True):
				self.mapped('move_id')._check_balanced()
			return result


class Almacen(models.Model):
	_inherit='stock.warehouse'
	auto_recepcion=fields.Boolean()
	stock_visible=fields.Boolean()


class Company(models.Model):
	_inherit='res.company'
	orden_compra=fields.Boolean()

class Compra(models.Model):
	_inherit='purchase.order'

	def boton_confirmar(self):
		self.button_confirm()
		if(self.picking_type_id.warehouse_id.auto_recepcion):
			sta = self.picking_ids.mapped('state')
			for pi in self.picking_ids.filtered(lambda x:x.state!='cancel'):
				if pi.state == 'assigned':
					pi.action_confirm()
					pi.move_lines._action_assign()
					pi.action_assign()
					return pi.button_validate()
				if pi.state in ('waiting','confirmed'):
					view = self.env.ref('orden_compra.purchase_order_alerta_view')
					wiz = self.env['purchase.order.alerta'].create({'mensaje': 'Sin stock disponible'})
					return {
						'alerta': True,
						'name': _('Alerta'),
						'type': 'ir.actions.act_window',
						'view_mode': 'form',
						'res_model': 'purchase.order.alerta',
						'views': [(view.id, 'form')],
						'view_id': view.id,
						'target': 'new',
						'res_id': wiz.id,
						'context': self.env.context,
					}

class AlertaDescuento(models.TransientModel):
	_name = 'purchase.order.alerta'
	_description = 'Alerta'

	mensaje = fields.Text(string='Mensaje')