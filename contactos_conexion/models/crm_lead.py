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

    lugar_trabajo = fields.Char(
        string="Lugar trabajo",
        store=True
    )
    nombre_establecimiento = fields.Char(
        string="Nombre establecimiento",
        store=True
    )
    razon_social = fields.Char(
        string="Razon social",
        store=True
    )
    direccion_comercial = fields.Char(
        string="Dirección comercial",
        store=True
    )
    proviene_de_iniciativa = fields.Boolean(
        string="Proviene de iniciativa",
        store=True,
        default=False
    )
    fecha_convertida_oportunidad = fields.Datetime(
        string="Fecha en que fue convertida a oportunidad",
        store=True
    )
    tiempo_de_conversion = fields.Integer(
        string="Tiempo iniciativa a oportunidad",
        store=True,
        default=0
    )
    tiempo_en_ganar_dias = fields.Integer(
        string="Días en ganar oportunidad",
        store=True,
        default=0
    )
    ticket_nuevo_cliente = fields.One2many(
        comodel_name='helpdesk.ticket',
        inverse_name='origin_crm'
    )

    def write(self, values):
        if 'date_conversion' in values:
            values['tiempo_de_conversion'] = int((values['date_conversion'] - self.create_date).days)
            values['proviene_de_iniciativa'] = True
        res = super(CRM, self).write(values)
        return res

    """
    @api.onchange('date_conversion')
    def cambia_date_conversion(self):
        if self.date_conversion:
            self.tiempo_de_conversion = int((self.date_conversion - self.create_date).days)
    """

    @api.onchange('partner_id')
    def cambia_parter_id(self):
        if self.partner_id.id:
            today_date = datetime.datetime.strptime(datetime.date.today().strftime("%m-%d-%Y %H:%M:%S"),
                                                    '%m-%d-%Y %H:%M:%S') + relativedelta(hours=+ 6)
            fecha_creacion = datetime.datetime.strptime(self.partner_id.create_date.strftime("%m-%d-%Y %H:%M:%S"),
                                                        '%m-%d-%Y %H:%M:%S') + relativedelta(hours=+ 6)
            tiempo_en_ganar = int((today_date - fecha_creacion).days)
            if tiempo_en_ganar == 0:
                self.partner_id.oprotunidad_origen = self.id
                self.partner_id.creado_desde_oportunidad = True
                self.partner_id.active = False
                display_msg = "Solicitud de nuevo cliente creado a traves de oportunidad"
                self.env['helpdesk.ticket'].create({
                    'name': 'Solicitud de creación de cliente',
                    'partner_id': self.partner_id.id,
                    'origin_crm': self.id,
                    'description': display_msg,
                    # 'tag_ids': (4, 1),
                    'team_id': 3
                })

    @api.onchange('stage_id')
    def tiempo_que_llevo_ganar_oportunidad(self):
        if self.stage_id.id and self.stage_id.id == 4:
            today_date = datetime.datetime.strptime(datetime.date.today().strftime("%m-%d-%Y %H:%M:%S"),
                                                    '%m-%d-%Y %H:%M:%S') + relativedelta(hours=+ 6)
            fecha_creacion = datetime.datetime.strptime(self.create_date.strftime("%m-%d-%Y %H:%M:%S"),
                                                        '%m-%d-%Y %H:%M:%S') + relativedelta(hours=+ 6)
            tiempo_en_ganar = int((today_date - fecha_creacion).days)
            # _logger.info('today_date: ' + str(today_date))
            # _logger.info('fecha_creacion:' + str(fecha_creacion))
            # _logger.info("tiempo_en_ganar: " + str(tiempo_en_ganar))
            self.tiempo_en_ganar_dias = tiempo_en_ganar

    def agrega_dias_write_date(self):
        write_date = self.write_date.strftime("%d-%m-%Y %H:%M:%S")
        _logger.info("write_date: " + str(write_date))
        date_1 = (datetime.datetime.strptime(write_date, '%d-%m-%Y %H:%M:%S') + relativedelta(days=+ 16))
        _logger.info("date_1: " + str(date_1))
        self.env.cr.execute("update crm_lead set write_date = '" + str(date_1) + "' where  id = " + str(self.id) + ";")

    def agrega_meses_write_date(self):
        date_1 = (datetime.datetime.strptime(self.write_date.strftime("%m-%d-%Y %H:%M:%S"),
                                             '%m-%d-%Y %H:%M:%S') + relativedelta(days=+ 181))
        _logger.info("date_1: " + str(date_1))
        self.env.cr.execute("update crm_lead set write_date = '" + str(date_1) + "' where  id = " + str(self.id) + ";")

    def decrmenta_dias_write_date(self):
        date_1 = (datetime.datetime.strptime(self.write_date.strftime("%m-%d-%Y %H:%M:%S"),
                                             '%m-%d-%Y %H:%M:%S') + relativedelta(days=- 16))
        _logger.info("date_1: " + str(date_1))
        self.env.cr.execute("update crm_lead set write_date = '" + str(date_1) + "' where  id = " + str(self.id) + ";")


"""
class CRMWizard(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'
    _description = 'Cambios'

    def action_apply(self):
        res = super(CRMWizard, self).action_apply()
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz)
        fecha = pytz.utc.localize(datetime.datetime.now()).astimezone(user_tz)
        result_opportunities = self.env['crm.lead'].browse(self._context.get('active_ids', []))
        for oportunidad in result_opportunities:
            try:
                oportunidad.proviene_de_iniciativa = True
                oportunidad.fecha_convertida_oportunidad = datetime.datetime.strptime(fecha.strftime("%m-%d-%Y %H:%M:%S"),
                                                                                      '%m-%d-%Y %H:%M:%S') + relativedelta(
                    hours=+ 6)
                oportunidad.tiempo_de_conversion = int((oportunidad.fecha_convertida_oportunidad - oportunidad.create_date).days)
                oportunidad.tiempo_de_conversion = int((oportunidad.date_conversion - oportunidad.create_date).days)
            except:
                _logger.info("error......................................")
        return res
"""


class CRM_TEAM(models.Model):
    _inherit = 'crm.team'

    invoiced_target = fields.Float(
        string="Meta de facturación",
        store=False,
        compute='_compute_meta_facturacion'
    )

    def _compute_meta_facturacion(self):
        for rec in self:
            totales = self.env['sale.order'].search(
                [
                    ('team_id', '=', rec._origin.id),
                    ('state', '=', 'sale')
                ]
            ).mapped('amount_total')
            suma_totales = 0
            for total in totales:
                suma_totales += total
            rec.invoiced_target = suma_totales