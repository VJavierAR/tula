from odoo import api, models, tools

import logging
import threading

_logger = logging.getLogger(__name__)


class SaleReportUpdate(models.TransientModel):
	_name='sale.report.update'
	_description='Update sale lines in report'



	def run(self):
		#pi=self.env['stock.picking'].search([['state','in',('waiting','confirmed')]],order='scheduled_date asc')
		#for pick in pi:
		#	pi.action_assign()
		action = self.env.ref('sale.action_order_report_all').read()[0]
		sl=self.env['sale.order.line'].search([['qty_invoiced','=',0]])
		for sa in sl:
			sl.f()
		return action
	
	def cancel(self):
		action = self.env.ref('sale.action_order_report_all').read()[0]
		return action

