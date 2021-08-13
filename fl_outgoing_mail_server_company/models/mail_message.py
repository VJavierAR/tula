# -*- coding: utf-8 -*-

from odoo import api, models


class Message(models.Model):
    _inherit = 'mail.message'

    @api.model
    def create(self, values):
        company = self.env.company or False
        if company:
            mail_server_id = self.env['ir.mail_server'].sudo().search([('company_id', '=', company.id)])
            if mail_server_id:
                email_from = '%s <%s>' % (company.name, mail_server_id.smtp_user)
                reply_to = '%s <%s>' % (company.name, company.email or mail_server_id.smtp_user)
                values.update({'mail_server_id': mail_server_id.id, 'email_from': email_from, 'reply_to': reply_to})
        res = super(Message, self).create(values)
        return res
