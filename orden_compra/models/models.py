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
	costo=fields.Float(related='product_id.standard_price',store=True,readonly=True,company_dependent=True,check_company=True)
	precio=fields.Float(related='product_id.lst_price',store=True,readonly=True, company_dependent=True,check_company=True)
	ultimo_provedor=fields.Many2one('res.partner',store=True,readonly=True)
	ultimo_precio_compra=fields.Float(store=True,readonly=True)
	stock_total=fields.Float(store=True,readonly=True)
	stock_quant=fields.Many2many('stock.quant',store=True,readonly=True)
	nueva_utilidad=fields.Float()
	utilida=fields.Float(related='product_id.x_studio_utilidad_precio_de_venta',store=True,readonly=True, company_dependent=True,check_company=True)
	nuevo_costo=fields.Float(store=True,readonly=True)
	nuevo_precio=fields.Float(compute='_nuevaUtil',store=True,readonly=True,default=0)
	valorX=fields.Float(compute='_ultimoProvedor',readonly=True)

	@api.depends('product_id','price_unit','quantity')
	def _ultimoProvedor(self):
		for record in self:
			record.valorX=1
			_logger.info('1')
			if(record.product_id.id!=False):
				ultimo=self.env['purchase.order.line'].search([['product_id','=',record.product_id.id]],order='date_planned desc',limit=1)
				record.ultimo_provedor=ultimo.order_id.partner_id.id
				record.ultimo_precio_compra=ultimo.price_unit
				wa=self.env['stock.warehouse'].search([['stock_visible','=',True]])
				quant=self.env['stock.quant'].search([['location_id','in',wa.mapped('lot_stock_id.id')],['product_id','=',record.product_id.id]])
				record.stock_quant=[(5,0,0)]
				record.stock_quant=[(6,0,quant.mapped('id'))]
				record.stock_total=sum(quant.mapped('quantity'))
				cost=self.env['stock.valuation.layer'].search([['product_id','=',record.product_id.id]])
				unidades=sum(cost.mapped('quantity'))+record.quantity
				costos=sum(cost.mapped('value'))+(record.price_unit*record.quantity)
				_logger.info('2')
				new_cost=costos/unidades if(unidades>0) else record.costo
				record.nuevo_costo=new_cost
				record.nuevo_precio=record.precio if(record.nuevo_precio==0) else record.nuevo_precio

	@api.depends('nueva_utilidad')
	def _nuevaUtil(self):
		for record in self:
			if(record.product_id.id!=False):
				if(record.nueva_utilidad!=0):
					_logger.info('3')
					_logger.info('4'+str(record.nueva_utilidad))
					record.valorX=record.nueva_utilidad
					newprice=(record.nuevo_costo * record.nueva_utilidad / 100) + record.nuevo_costo
					record.nuevo_precio=newprice
					record.nueva_utilidad=record.valorX
					#record.nueva_utilidad=((record.nuevo_precio-record.nuevo_costo)/newprice)*100 if(newprice!=0) else 0


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