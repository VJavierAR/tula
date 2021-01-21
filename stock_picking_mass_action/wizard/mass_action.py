from odoo import _,fields, api,models
from odoo.models import TransientModel
import datetime, time
from odoo.exceptions import UserError,RedirectWarning
from odoo.tools.float_utils import float_compare


class pickingDesasignar(TransientModel):
    _name='picking.desasignar'
    _description='desasignar series'
    solicitud=fields.Many2one('sale.order')
