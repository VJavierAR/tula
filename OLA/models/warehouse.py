from odoo import models, fields, api,_
from odoo import exceptions

class almacen(models.Model):
	_inherit='stock.warehouse'
	code = fields.Char('Short Name', required=True, help="Short name used to identify your warehouse")

class stock(models.Model):
	_inherit = 'stock.picking'
	#en_proceso=fields.Boolean(default=False)
	state = fields.Selection(selection_add=[('printed', 'Impreso')])
    user_print_id = fields.Many2one(comodel_name="res.users", string="Usuario que imprimió", tracking=True, copy=False, required=False)
    user_validate_id = fields.Many2one(comodel_name="res.users", string="Usuario que validó", tracking=True, copy=False, required=False)
	#@api.multi
	def print_vale_de_entrega(self):
		if(self.state=='printed'):
			raise exceptions.UserError('Orden de surtido ya se encunetra en proceso')			
		else:
			self.state='printed'
			self.user_print_id=self.env.user.id
			return self.env.ref("stock.action_report_picking").report_action(self)