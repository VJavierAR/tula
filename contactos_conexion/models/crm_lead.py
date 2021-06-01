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
        date_1 = (datetime.datetime.strptime(self.write_date.strftime("%m-%d-%Y %H:%M:%S"), '%m-%d-%Y %H:%M:%S') + relativedelta(days=+ 15))
        _logger.info("date_1: " + str(date_1))
        self.env.cr.execute("update crm_lead set write_date = '" + str(date_1) + "' where  id = " + str(self.id) + ";")
        self.conexis = True

    def agrega_meses_write_date(self):
        date_1 = (datetime.datetime.strptime(self.write_date.strftime("%m-%d-%Y %H:%M:%S"),
                                             '%m-%d-%Y %H:%M:%S') + relativedelta(days=+ 180))
        _logger.info("date_1: " + str(date_1))
        self.env.cr.execute("update crm_lead set write_date = '" + str(date_1) + "' where  id = " + str(self.id) + ";")
