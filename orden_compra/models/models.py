# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging, ast
_logger = logging.getLogger(__name__)


class Factura(models.Model):
	_inherit='account.move'


	def action_post(self):
		if self.filtered(lambda x: x.journal_id.post_at == 'bank_rec').mapped('line_ids.payment_id').filtered(lambda x: x.state != 'reconciled'):
			raise UserError(_("A payment journal entry generated in a journal configured to post entries only when payments are reconciled with a bank statement cannot be manually posted. Those will be posted automatically after performing the bank reconciliation."))
		if self.env.context.get('default_type'):
			context = dict(self.env.context)
			tipo=context['default_type']
			if(tipo=='in_invoice'):
				for inv in self.invoice_line_ids:
					_logger.info(inv.id)
					_logger.info(str(inv.default_get(('product_id','id'))))
			del context['default_type']
			self = self.with_context(context)
		return self.post()



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
	order_compra=fields.Boolean()