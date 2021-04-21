from odoo import models, fields, api,_
from odoo import exceptions

class almacen(models.Model):
	_inherit='stock.warehouse'
	code = fields.Char('Short Name', required=True, help="Short name used to identify your warehouse")

class stock(models.Model):
	_inherit = 'stock.picking'
	en_proceso=fields.Boolean(default=False)

	#@api.multi
	def print_vale_de_entrega(self):
		if(self.en_proceso):
			raise exceptions.UserError("No se puede validar la orden dado que el Cliente: "+self.cliente.name+' no cuenta con ubicaciones disponibles o no tiene ningun servicio contratado.')			
		else:
			self.en_proceso=True
			return self.env.ref("stock.action_report_picking").report_action(self)