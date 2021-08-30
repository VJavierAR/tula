# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import logging, ast
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError
from statistics import mean

class Factura(models.Model):
	_inherit='account.move'
	almacen=fields.Many2one('stock.warehouse')
	orden_compra=fields.Many2one('purchase.order')
	check=fields.Boolean(related='company_id.orden_compra')
	otro=fields.Boolean(compute='checkSa')
	checkAlmacen=fields.Boolean()


	@api.depends('check')
	def checkSa(self):
		for record in self:
			record.otro='default_purchase_id' in self.env.context
			if(check.almacen==False):
				if(self.type=='in_invoice'):
					self.almacen=self.env['stock.warehouse'].search([],limit=1,order='id asc').id
					self.checkAlmacen=True
					
	def action_post(self):
		if self.filtered(lambda x: x.journal_id.post_at == 'bank_rec').mapped('line_ids.payment_id').filtered(lambda x: x.state != 'reconciled'):
			raise UserError(_("A payment journal entry generated in a journal configured to post entries only when payments are reconciled with a bank statement cannot be manually posted. Those will be posted automatically after performing the bank reconciliation."))
		if self.env.context.get('default_type'):
			context = dict(self.env.context)
			tipo=context['default_type']
			del context['default_type']
			self = self.with_context(context)
			if(tipo!='in_invoice'):
				self.post()
			if(tipo=='in_invoice'):
				produ=self.invoice_line_ids.mapped('product_id')
				if(len(self.invoice_line_ids)!=len(produ)):
					raise UserError(_('Faltan productos en las lineas de Factura'))
				else:
					self.post()
			if(tipo=='in_invoice' and self.company_id.orden_compra and self.purchase_id.id==False):
				orden=self.env['purchase.order'].create({'partner_id':self.partner_id.id,'picking_type_id':self.almacen.in_type_id.id,'check':True if(self.company_id.price_lst) else False})
				for inv in self.invoice_line_ids:
					prod=dict()
					prod['product_id']=inv.product_id.id
					prod['product_qty']=inv.quantity
					prod['name']=inv.name
					prod['price_unit']=inv.price_subtotal/inv.quantity if(inv.quantity!=0) else 0
					prod['taxes_id']=inv.tax_ids.mapped('id')
					prod['order_id']=orden.id
					prod['product_uom']=inv.product_uom_id.id
					prod['date_planned']=inv.date
					if(self.company_id.price_lst):
						prod['precio_impuesto']=inv.valorX
						prod['utilidad_venta']=inv.nueva_utilidad
						prod['precio_lista']=inv.nuevo_precio
					p=self.env['purchase.order.line'].create(prod)
					p.write({'invoice_lines':[(6,0,inv.mapped('id'))]})
				orden.write({'invoice_ids':[(6,0,self.mapped('id'))]})
				self.write({'purchase_id':orden.id,'invoice_origin':orden.name,'orden_compra':orden.id})
				orden._compute_invoice()
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
				orden=self.orden_compra
				orden.write({'invoice_ids':[(5,0,0)]})
				if(orden.picking_type_id.warehouse_id.auto_recepcion):
					for pi in self.orden_compra.picking_ids:
						rp=self.env['stock.return.picking'].create({'picking_id':pi.id})
						rp._onchange_picking_id()
						for wizard in rp:
							new_picking_id, pick_type_id = wizard._create_returns()
						p=self.env['stock.picking'].browse(new_picking_id)
						p.action_confirm()
						p.move_lines._action_assign()
						p.action_assign()
						return p.button_validate()
					self.write({'invoice_origin':'','orden_compra':False})
				else:
					self.write({'invoice_origin':''})
					for pi in self.orden_compra.picking_ids:
						pi.unlink()
					self.orden_compra.write({'state': 'cancel'})
					self.orden_compra.unlink()
	
	def action_view_purchase(self):
		action = self.env.ref('purchase.purchase_form_action').read()[0]
		form_view = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
		if 'views' in action:
			action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
		else:
			action['views'] = form_view
		action['res_id'] = self.orden_compra.id
		return action

class LinesFactura(models.Model):
	_inherit='account.move.line'
	costo=fields.Float()
	precio=fields.Float()
	ultimo_provedor=fields.Many2one('res.partner',)
	ultimo_precio_compra=fields.Float()
	stock_total=fields.Float()
	stock_quant=fields.Many2many('stock.quant',)
	nueva_utilidad=fields.Float(store=True)
	utilida=fields.Float()
	nuevo_costo=fields.Float()
	nuevo_precio=fields.Float(store=True)
	valorX=fields.Float()
	impuesto=fields.Float(default=0)

	#@api.onchange('product_id')
	#def _compute_amount(self):
	#	for line in self:
			# price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
			# taxes = line.product_id.taxes_ids.compute_all(price, line.move_id.currency_id, 1, product=line.product_id, partner=line.move_id.partner_id)
			# line.impuesto=0
			# if(len(line.tax_ids)>0):
			# 	t=float(taxes['taxes'][0]['amount'])
			# 	line.impuesto=t
	
	@api.onchange('product_id','price_unit','quantity')
	def _ultimoProvedor(self):
		for record in self:
			record.valorX=0
			if(record.product_id.id!=False):
				record.costo=record.product_id.with_context(force_company=self.env.company.id).standard_price if(record.product_id.with_context(force_company=self.env.company.id).standard_price!=0) else record.product_id.with_context(force_company=self.env.company.id).product_tmpl_id.standard_price
				record.precio=record.product_id.with_context(force_company=self.env.company.id).lst_price if(record.product_id.with_context(force_company=self.env.company.id).lst_price!=0) else record.product_id.with_context(force_company=self.env.company.id).product_tmpl_id.lst_price 
				record.utilida=record.product_id.with_context(force_company=self.env.company.id).x_studio_utilidad_precio_de_venta if(record.product_id.with_context(force_company=self.env.company.id).x_studio_utilidad_precio_de_venta!=0) else record.product_id.with_context(force_company=self.env.company.id).product_tmpl_id.x_studio_utilidad_precio_de_venta
				ultimo=self.env['purchase.order.line'].search([['product_id','=',record.product_id.id]],order='date_planned desc',limit=1)
				record.ultimo_provedor=ultimo.order_id.partner_id.id
				record.ultimo_precio_compra=ultimo.price_unit*ultimo.currency_id.rate
				wa=self.env['stock.warehouse'].search([['stock_visible','=',True]])
				location=self.env['stock.location'].search([['location_id','in',wa.mapped('lot_stock_id.id')],['usage','=','internal']]).mapped('id') if(wa.mapped('lot_stock_id.id')!=[]) else []
				locations=wa.mapped('lot_stock_id.id')+location
				quant=self.env['stock.quant'].search([['location_id','in',locations],['product_id','=',record.product_id.id]])
				record.stock_quant=[(5,0,0)]
				record.stock_quant=[(6,0,quant.mapped('id'))]
				record.stock_total=sum(quant.mapped('quantity'))
				cost=self.env['stock.valuation.layer'].search([['product_id','=',record.product_id.id]])
				#old
				unidades=sum(cost.mapped('quantity'))+record.quantity
				costos=sum(cost.mapped('value'))+(record.price_subtotal)
				#new
				# unidades=2
				# costos=(record.product_id.nuevo_costo_facturacion_impuesto)+(record.price_unit+record.impuesto)
				#######
				new_cost=costos/unidades if(unidades>0) else record.costo
				record.nuevo_costo=new_cost
				record.nuevo_precio=record.precio
				record.nueva_utilidad=record.nueva_utilidad if(record.nueva_utilidad!=0) else record.utilida
				#newprice=(record.nuevo_costo * record.nueva_utilidad / 100) + record.nuevo_costo
				newprice=((record.price_unit * record.nueva_utilidad) / 100) + record.price_unit
				record.nuevo_precio=newprice
				record.valorX=record.nuevo_precio

	@api.onchange('nuevo_precio')
	def _nuevaUtil(self):
		#self._ultimoProvedor()
		for record in self:
			if(record.product_id.id!=False):
				#record.nueva_utilidad=((record.nuevo_precio-record.nuevo_costo)*100)/record.nuevo_costo if(record.nuevo_costo!=0) else 0
				precio=record.price_subtotal/record.quantity
				#record.nueva_utilidad=((record.nuevo_precio-record.price_unit)*100)/record.price_unit if(record.price_unit!=0) else 0
				record.nueva_utilidad=((record.nuevo_precio-precio)*100)/precio if(precio!=0) else 0


	@api.onchange('nueva_utilidad')
	def _nuevaPreci(self):
		#self._ultimoProvedor()
		for record in self:
			if(record.product_id.id!=False):
				#newprice=(record.nuevo_costo * record.nueva_utilidad / 100) + record.nuevo_costo
				precio=record.price_subtotal/record.quantity
				newprice=((precio * record.nueva_utilidad) / 100) + precio
				#newprice=((record.price_unit * record.nueva_utilidad) / 100) + record.price_unit
				taxes = record.product_id.taxes_id.compute_all(newprice, record.move_id.currency_id, 1, product=record.product_id, partner=record.move_id.partner_id)
				record.impuesto=0
				if(len(record.product_id.taxes_id)>0):
					t=float(taxes['taxes'][0]['amount'])
					record.impuesto=t
				##Hi
				##precio=record.price_unit+record.impuesto
				###newprice=(precio * record.nueva_utilidad / 100) + precio
				record.nuevo_precio=newprice
				record.valorX=newprice+record.impuesto

	@api.onchange('valorX')
	def _precioSinImpuesto(self):
		for record in self:
			if(record.product_id.id!=False and record.valorX!=0):
				taxes = sum(record.product_id.taxes_id.mapped('amount'))
				record.nuevo_precio=record.valorX/(1+(taxes/100))

	def create(self,list_vals):
		for vals in list_vals:
			if('product_id' in vals and self.company_id.price_lst):
				if(vals['product_id']!=False):
					nueva=vals['nueva_utilidad'] if('nueva_utilidad' in vals) else 0
					precio=vals['nuevo_precio'] if('nuevo_precio' in vals) else 0
					producto=vals['product_id'] if('product_id' in vals) else self.product_id.id
					precio_impuesto=vals['valorX'] if('valorX' in vals) else 0
					if(producto):
						p=self.env['product.product'].browse(producto)
						c=vals['credit'] if('credit' in vals) else self.credit
						if(p.x_studio_utilidad_precio_de_venta!=nueva and c==0):
							p.write({'x_studio_utilidad_precio_de_venta':nueva,'lst_price':precio,'nuevo_costo_facturacion_impuesto':precio_impuesto})
							p.product_tmpl_id.write({'x_studio_utilidad_precio_de_venta':nueva,'lst_price':precio,'nuevo_costo_facturacion_impuesto':precio_impuesto})
							p._compute_x_preciominimo()
							p.product_tmpl_id._compute_x_preciominimo()
							#p.cambio_precio_de_venta()
		lines = super(LinesFactura, self).create(list_vals)
		return lines

	def write(self,vals):
		result = True
		for line in self:
			producto=vals['product_id'] if('product_id' in vals) else line.product_id.id
			nueva=vals['nueva_utilidad'] if('nueva_utilidad' in vals) else line.nueva_utilidad
			precio=vals['nuevo_precio'] if('nuevo_precio' in vals) else line.nuevo_precio
			precio_impuesto=vals['valorX'] if('valorX' in vals) else line.valorX
			if(producto and self.company_id.price_lst):
				p=self.env['product.product'].browse(producto)
				c=vals['credit'] if('credit' in vals) else line.credit
				if(p.x_studio_utilidad_precio_de_venta!=nueva and c==0):
					p.write({'x_studio_utilidad_precio_de_venta':nueva,'lst_price':precio,'nuevo_costo_facturacion_impuesto':precio_impuesto})
					p.product_tmpl_id.write({'x_studio_utilidad_precio_de_venta':nueva,'lst_price':precio,'nuevo_costo_facturacion_impuesto':precio_impuesto})
					p._compute_x_preciominimo()
					p.product_tmpl_id._compute_x_preciominimo()
			result |= super(LinesFactura, line).write(vals)
		return result
					






