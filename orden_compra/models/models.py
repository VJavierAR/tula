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
				orden.button_confirm()
				orden.write({'invoice_ids':[(6,0,self.mapped('id'))]})
				self.write({'purchase_id':orden.id,'invoice_origin':orden.name,'orden_compra':orden.id})
				orden._compute_invoice()
			del context['default_type']
			self = self.with_context(context)
		return self.post()

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
		if(tipo=='in_invoice' and self.company_id.orden_compra):
			if(self.orden_compra.mapped('id')!=[]):
				self.write({'invoice_origin':''})
				for pi in self.orden_compra.picking_ids:
					pi.unlink()
				self.orden_compra.write({'state': 'cancel'})
				self.orden_compra.unlink()

class LinesFactura(models.Model):
	_inherit='account.move.line'
	costo=fields.Float(related='product_id.standard_price')
	precio=fields.Float(related='product_id.lst_price')
	ultimo_provedor=fields.Many2one('res.partner')
	ultimo_precio_compra=fields.Float()






class Almacen(models.Model):
	_inherit='stock.warehouse'
	auto_recepcion=fields.Boolean()
	stock_visible=fields.Boolean()


class Company(models.Model):
	_inherit='res.company'
	orden_compra=fields.Boolean()

class Compra(models.Model):
	_inherit='purchase.order'

	def button_approve(self, force=False):
		self.write({'state': 'purchase', 'date_approve': fields.Datetime.now()})
		self.filtered(lambda p: p.company_id.po_lock == 'lock').write({'state': 'done'})
		_logger.info(str(self.picking_ids.mapped('id')))
		return {}


