from odoo import fields, api
from odoo.models import TransientModel
import logging, ast
import datetime, time
import pytz
import io,csv
import datetime
import xlsxwriter
import base64
import xmlrpc.client
from datetime import date
from odoo.exceptions import UserError
from odoo import exceptions, _

_logger = logging.getLogger(__name__)


class TestReport(TransientModel):
    _name = 'account.correo'
    _description = 'Tramite'
   
    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')

    def _default_move_ids(self):
        return self.env['account.move'].browse(self.env.context.get('active_ids'))

    move_ids = fields.Many2many(
        string = 'Tickets',
        comodel_name = "account.move",
        default = lambda self: self._default_move_ids(),
        help = "",
    )

    def mensaje(self):       
        pal=''
        for move in self.move_ids:
            mail_template = self.env['mail.template'].search([('id', '=', 52)])
            if mail_template:
               mail_template.write({
                    'email_to': move.partner_id.correoFac,
                    })             
            sen=self.env['mail.template'].browse(mail_template.id).send_mail(move.partner_id.id,force_send=True)             
            if sen:
                move.write({'tramite':'tramitado'})
        #raise exceptions.ValidationError(str(self.move_ids))