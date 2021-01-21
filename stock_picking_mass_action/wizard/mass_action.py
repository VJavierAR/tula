from odoo import _,fields, api,models
from odoo.models import TransientModel
import datetime, time
from odoo.exceptions import UserError,RedirectWarning
from odoo.tools.float_utils import float_compare


class pickingDesasignar(TransientModel):
	_name='picking.desasignar'
	_description='desasignar series'
	pick_ids = fields.Many2many('stock.picking')
	estado = fields.Many2one('detalle.move','Detalle')
	cancel_backorder=fields.Boolean(default=True)

	def confirm(self):
		self.picking_id.move_ids_without_package.write({'estado':self.estado})
		if(self.cancel_backorder):
			self.picking_id.action_cancel()



class BckorderCancel():
	_inherit='stock_backorder_confirmation'

	def process_cancel_backorder(self):
		self._process(cancel_backorder=True)
		w=self.env['picking.desasignar'].create({'picking_id':self.pick_ids,'cancel_backorder':False})
		view=self.env.ref('stock.view_picking_desasignar')
		return {
				'name': _('Motivos de Cancelacion'),
				'type': 'ir.actions.act_window',
				'res_model': 'picking.desasignar',
				'view_type': 'form',
				'view_mode': 'form',
				'res_id':w.id,
				'views': [(view.id, 'form')],
				'view_id': view.id,
				'target':'new'
				}