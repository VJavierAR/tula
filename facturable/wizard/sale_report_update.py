from odoo import api, models, tools

import logging
import threading
import datetime
_logger = logging.getLogger(__name__)


class SaleReportUpdate(models.TransientModel):
	_name='sale.report.update'
	_description='Update sale lines in report'



	def run(self):
		#pi=self.env['stock.picking'].search([['state','in',('waiting','confirmed')]],order='scheduled_date asc')
		#for pick in pi:
		#	pi.action_assign()
		action = self.env.ref('sale_enterprise.sale_report_action_dashboard').read()[0]
		sl=self.env['sale.order.line'].search([['qty_invoiced','=',0],['facturable','=',0]],limit=100,order='id desc')
		_logger.info('REGISTROS:'+str(len(sl)))
		for sa in sl:
			sl.f()
		return action
	
	def cancel(self):
		action = self.env.ref('sale_enterprise.sale_report_action_dashboard').read()[0]
		return action

