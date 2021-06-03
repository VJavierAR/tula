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

    def conect(self):
        task = {"username": username_login, "password": password_login}
        resp = requests.post(url_login, json=task)
        if resp.status_code == status_code_correct:
            json_respuesta = resp.json()
            _logger.info(json_respuesta)
            if json_respuesta['error'] == no_error_token:
                global token
                token = json_respuesta['idToken']
                _logger.info(token)
                # self.creaar_cliente_naf()
        else:
            _logger.info("Error al realizar petición")



    def agrega_dias_write_date(self):
        self.conexis = True
        date_1 = (datetime.datetime.strptime(self.write_date.strftime("%m-%d-%Y %H:%M:%S"), '%m-%d-%Y %H:%M:%S') + relativedelta(days=+ 15))
        _logger.info("date_1: " + str(date_1))
        self.env.cr.execute("update crm_lead set write_date = '" + str(date_1) + "' where  id = " + str(self.id) + ";")

    def agrega_meses_write_date(self):
        date_1 = (datetime.datetime.strptime(self.write_date.strftime("%m-%d-%Y %H:%M:%S"),
                                             '%m-%d-%Y %H:%M:%S') + relativedelta(days=+ 180))
        _logger.info("date_1: " + str(date_1))
        self.env.cr.execute("update crm_lead set write_date = '" + str(date_1) + "' where  id = " + str(self.id) + ";")

    def decrmenta_dias_write_date(self):
        date_1 = (datetime.datetime.strptime(self.write_date.strftime("%m-%d-%Y %H:%M:%S"),
                                             '%m-%d-%Y %H:%M:%S') + relativedelta(days=- 15))
        _logger.info("date_1: " + str(date_1))
        self.env.cr.execute("update crm_lead set write_date = '" + str(date_1) + "' where  id = " + str(self.id) + ";")


class CRMWizard(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'
    _description = 'Cambios'

    def action_apply(self):
        res = super(CRMWizard, self).action_apply()
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz)
        fecha = pytz.utc.localize(datetime.datetime.now()).astimezone(user_tz)
        result_opportunities = self.env['crm.lead'].browse(self._context.get('active_ids', []))
        for oportunidad in result_opportunities:
            oportunidad.proviene_de_iniciativa = True
            oportunidad.fecha_convertida_oportunidad = datetime.datetime.strptime(fecha.strftime("%m-%d-%Y %H:%M:%S"),
                                                                                  '%m-%d-%Y %H:%M:%S') + relativedelta(
                hours=+ 6)
            oportunidad.tiempo_de_conversion = int((oportunidad.fecha_convertida_oportunidad - oportunidad.create_date).days)
        return res
