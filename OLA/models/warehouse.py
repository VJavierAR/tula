from odoo import models, fields, api,_


class almacen(models.Model):
	_inherit='stock.warehouse'
	code = fields.Char('Short Name', required=True, help="Short name used to identify your warehouse")

class stock(models.Model):
	_inherit = 'stock.picking'
	en_proceso=fields.Boolen(default=False)

	#@api.multi
	def print_vale_de_entrega(self):
		self.en_proceso=True
		return self.env.ref("stock.report_deliveryslip").report_action(self)