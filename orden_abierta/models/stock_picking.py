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

    def cron_notificacion_salidas(self):
        estados = ['assigned']
        ordenes_entrega = self.search([
            ('state', 'in', estados),
        ])
        usuarios = self.env['res.groups'].sudo().search(
            [("name", "=", "Notificaciones de ordenes abiertas")]).mapped('users')

        for orden in ordenes_entrega:
            notification_ids = []
            for usuario in usuarios:
                notification_ids.append((0, 0, {
                    'res_partner_id': usuario.partner_id.id,
                    'notification_type': 'inbox'}))
            orden.message_post(
                body='Se necesita validar orden',
                message_type='notification',
                subtype='mail.mt_comment',
                author_id=1,
                notification_ids=notification_ids)