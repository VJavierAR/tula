# -*- coding: utf-8 -*-

from odoo import models, fields, api
from email.utils import formataddr
from odoo.exceptions import UserError, RedirectWarning
from odoo import exceptions, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging, ast
import pytz
import base64
import requests
import json

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    _description = 'cron'

    def write(self, vals):
        if 'state' in vals and vals['state'] == 'done' and 'out' in self.name and self.sale_id.id and self.sale_id.user_id.id:
            vendedor_id = self.sale_id.user_id.id
            message_text = "Se necesita validar orden " + self.sale_id.name
            # odoo runbot
            odoobot_id = self.env['ir.model.data'].sudo().xmlid_to_res_id("base.partner_root")
            notificaciones = [(4, self.env.user.partner_id.id), (4, odoobot_id), (4, vendedor_id)]
            # find if a channel was opened for this user before
            channel = self.env['mail.channel'].sudo().search([
                ('name', '=', 'Alerta vendedores'),
                ('channel_partner_ids', 'in', [self.env.user.partner_id.id])
            ],
                limit=1,
            )

            if not channel:
                # create a new channel
                channel = self.env['mail.channel'].with_context(mail_create_nosubscribe=True).sudo().create({
                    'channel_partner_ids': notificaciones,
                    'public': 'private',
                    'channel_type': 'chat',
                    'email_send': False,
                    'name': f'Alerta vendedores',
                    'display_name': f'Alerta vendedores',
                })

            # send a message to the related user
            channel.sudo().message_post(
                body=message_text,
                author_id=odoobot_id,
                message_type="comment",
                subtype="mail.mt_comment",
            )

        result = super(StockPicking, self).write(vals)
        return result

    @api.onchange('state')
    def cambia_state(self):
        if self.state:
            if self.state == 'done' and 'out' in self.name and self.sale_id.id and self.sale_id.user_id.id:
                # usuarios = self.env['res.groups'].sudo().search(
                #    [("name", "=", "Notificacion a vendedor al validar picking")]).mapped('users')
                vendedor_id = self.sale_id.user_id.id

                message_text = "Se necesita validar orden " + self.sale_id.name
                # odoo runbot
                odoobot_id = self.env['ir.model.data'].sudo().xmlid_to_res_id("base.partner_root")
                notificaciones = [(4, self.env.user.partner_id.id), (4, odoobot_id), (4, vendedor_id)]
                # for usuario in usuarios:
                #    notificaciones.append([4, usuario.partner_id.id])

                # find if a channel was opened for this user before
                channel = self.env['mail.channel'].sudo().search([
                    ('name', '=', 'Alerta vendedores'),
                    ('channel_partner_ids', 'in', [self.env.user.partner_id.id])
                ],
                    limit=1,
                )

                if not channel:
                    # create a new channel
                    channel = self.env['mail.channel'].with_context(mail_create_nosubscribe=True).sudo().create({
                        'channel_partner_ids': notificaciones,
                        'public': 'private',
                        'channel_type': 'chat',
                        'email_send': False,
                        'name': f'Alerta vendedores',
                        'display_name': f'Alerta vendedores',
                    })

                # send a message to the related user
                channel.sudo().message_post(
                    body=message_text,
                    author_id=odoobot_id,
                    message_type="comment",
                    subtype="mail.mt_comment",
                )

    def cron_notificacion_salidas(self):
        estados = ['confirmed', 'assigned']
        ordenes_entrega = self.search([
            ('state', 'in', estados),
        ])
        usuarios = self.env['res.groups'].sudo().search(
            [("name", "=", "Notificaciones de picking a bodega")]).mapped('users')

        for orden in ordenes_entrega:

            message_text = "Se necesita validar orden " + orden.name
            # odoo runbot
            odoobot_id = self.env['ir.model.data'].sudo().xmlid_to_res_id("base.partner_root")

            notification_ids = []
            notificaciones = [(4, self.env.user.partner_id.id), (4, odoobot_id)]
            for usuario in usuarios:
                notification_ids.append((0, 0, {
                    'res_partner_id': usuario.partner_id.id,
                    'notification_type': 'inbox'}))
                notificaciones.append([4, usuario.partner_id.id])
            """
            orden.message_post(
                body='Se necesita validar orden',
                message_type='notification',
                subtype='mail.mt_comment',
                author_id=2,
                notification_ids=notification_ids)
            """


            # find if a channel was opened for this user before
            channel = self.env['mail.channel'].sudo().search([
                ('name', '=', 'Picking Validated'),
                ('channel_partner_ids', 'in', [self.env.user.partner_id.id])
            ],
                limit=1,
            )

            if not channel:
                # create a new channel
                channel = self.env['mail.channel'].with_context(mail_create_nosubscribe=True).sudo().create({
                    'channel_partner_ids': notificaciones,
                    'public': 'private',
                    'channel_type': 'chat',
                    'email_send': False,
                    'name': f'Picking Validated',
                    'display_name': f'Picking Validated',
                })

            # send a message to the related user
            channel.sudo().message_post(
                body=message_text,
                author_id=odoobot_id,
                message_type="comment",
                subtype="mail.mt_comment",
            )
