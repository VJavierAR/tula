# -*- coding: utf-8 -*-

from odoo import models, fields, api
from email.utils import formataddr
from odoo.exceptions import UserError, RedirectWarning
from odoo import exceptions, _
from dateutil.relativedelta import relativedelta
import logging, ast
import datetime, time
import pytz
import base64
import requests
_logger = logging.getLogger(__name__)


class CRM(models.Model):
    _inherit = 'crm.lead'
    _description = 'Cambios'

    ticket_validacion = fields.One2many(
        comodel_name="helpdesk.ticket",
        inverse_name="origen_crm",
        string="Tickets"
    )

    def write(self, vals):
        _logger.info("valores al escribir desde crm: \n" + str(vals))
        _logger.info("self: \n" + str(self))
        if 'partner_id' in vals:
            partner = self.env['res.partner'].search([
                ('id', '=', vals['partner_id'])
            ])
            oportunidades_donde_aparece = self.env['crm.lead'].search([
                ('partner_id', '=', vals['partner_id'])
            ])
            _logger.info('partner: ' + str(partner))
            _logger.info('oportunidades_donde_aparece: ' + str(oportunidades_donde_aparece))
            fecha_actual = datetime.datetime.now().date()
            fecha_creacion_cliente = partner.create_date.date()
            _logger.info('fecha_actual: ' + str(fecha_actual))
            _logger.info('fecha_creacion_cliente: ' + str(fecha_creacion_cliente))
            if fecha_creacion_cliente == fecha_actual and not oportunidades_donde_aparece:
                _logger.info("el cliente se creo hoy y no aparece en ninguna oportunidad: ")
                partner.active = False
                ticket = self.env['helpdesk.ticket'].create({
                    'name': 'Solicitud de visibilidad de cliente en Odoo',
                    'partner_id': partner.id,
                    'origen_crm': self.id,
                    'description': "Solicitud de visibilidad de cliente",
                })

        rec = super(CRM, self).write(vals)

        return rec
