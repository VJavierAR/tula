from odoo import _, fields, api
from odoo.models import Model
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
import logging, ast
_logger = logging.getLogger(__name__)
#puro aaa
class StockPicking(Model):
    _inherit = 'stock.picking'
    active = fields.Boolean('Active', default=True, track_visibility=True)

    def cancelacion(self):
        #self.action_cancel()
        w=self.env['picking.desasignar'].create({'pick_ids':[(4,self.id)]})
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


class StockPickingMove(Model):
    _inherit = 'stock.move'
    estado = fields.Many2one('detalle.move','Detalle')



class DetalleMove(Model):
    _name='detalle.move'
    name=fields.Char()