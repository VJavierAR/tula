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
from odoo.tools import email_re
import base64


_logger = logging.getLogger(__name__)


class TestReport(TransientModel):
    _name = 'account.correo'
    _description = 'Tramite'
    
    #_inherit = 'mail.compose.message'
   
    date_from = fields.Char(string='From',compute='_archivo_a',store=True)
    date_to = fields.Char(string='Para',store=True)
    body = fields.Char(string='body',store=True)
    subject = fields.Char(string='subject',store=True)
    attachment_ids=fields.Many2many('ir.attachment', string="attachment",store=True)
    
    def _default_move_ids(self):
        
        return self.env['account.move'].browse(self.env.context.get('active_ids'))
    
    

    move_ids = fields.Many2many(
        string = 'Tickets',
        comodel_name = "account.move",
        default = lambda self: self._default_move_ids(),
        help = "",
    )
    
        
    @api.onchange('date_from')
    def _archivo_a(self):        
        pdf = self.env.ref('facturacion.reporte_seguimiento')       
        
        
        pdf = self.env.ref('facturacion.reporte_de_seguimiento').sudo().render_qweb_pdf([self.move_ids[0].id])[0]
        a=self.env['ir.attachment'].create({
            'name': "reporteSeguimiento.pdf",
            'type': 'binary',
            'res_id': self.move_ids[0].id,
            'res_model': 'account.correo',
            'datas': base64.b64encode(pdf),
            'mimetype': 'application/x-pdf',
            
        })
        
        self.date_to=str(self.move_ids[0].partner_id.correoFac)
        self.date_from=''
        self.subject='Reporte de seguimiento .'
        self.body="<br>Dear  "+str(self.move_ids[0].partner_id.name)+",</br>Exception made if there was a mistake of ours, it seems that the following amount stays unpaid. Please, takeappropriate measures in order to carry out this payment in the next 8 days.Would your payment have been carried out after this mail was sent, please ignore this      message. Do not hesitateto contact our accounting department.Best Regards"
        self.attachment_ids=[(6,0,[a.id])]
    
    
    

    
    
    
    



        
        
        
        

        
    

    def mensaje(self):       
        pal=''
        re=[]        
        mail_template = self.env.ref('facturacion.reporte_seguimiento')
        clientes=[]
        for move in self.move_ids:                                                            
            clientes.append(move.partner_id.id)
            move.write({'tramite':'tramitadas'})
        finalL=set(clientes)    
        cli = self.env['res.partner']
        
        for send in finalL:
            cliente = cli.search([('id', '=', send)])
            vals={
                    'email_to': self.date_to,
                    'body_html': self.body,
                    'attachment_ids': self.attachment_ids,
                    'subject': self.subject
            }
            mail_id = self.env['mail.mail'].create(vals)
            mail_id.send()

