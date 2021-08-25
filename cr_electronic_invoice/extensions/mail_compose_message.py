# -*- coding: utf-8 -*-

from odoo import fields, models, api, tools

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'
    
    def send_mail(self, auto_commit=False):
        context = self._context
        if context.get('mass_mark_invoice_as_sent') and \
                context.get('default_model') == 'account.move':
            account_invoice = self.env['account.move']
            invoice_ids = context.get('active_ids')
            for invoice in account_invoice.browse(invoice_ids):
                invoice.invoice_sent = True
        return super(MailComposeMessage, self).send_mail(auto_commit=auto_commit)

class MailMail(models.Model):
    _inherit = 'mail.mail'

    def _send_prepare_values(self, partner=None):
        res = super(MailMail, self)._send_prepare_values(partner=partner)
        if self.model == "account.move":
            invoice_send = self.env['account.move'].search([('id', '=', self.res_id)], limit=1)
            if invoice_send.tipo_documento and partner.email_fe:
                res.update({'email_to': [tools.formataddr((partner.name or 'False', partner.email_fe or 'False'))]})
        return res

    