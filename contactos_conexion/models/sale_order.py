# -*- coding: utf-8 -*-

from odoo import models, fields, api
from email.utils import formataddr
from odoo.exceptions import UserError, RedirectWarning
from odoo import exceptions, _
import logging, ast
import datetime, time
import pytz
import base64
import requests

_logger = logging.getLogger(__name__)

token = ""
username_login = "apiodoo@promed-sa.com"
password_login = "ApiOdoo*001"
url_login = 'https://trxk539p2e.execute-api.us-east-1.amazonaws.com/prueba/Login'
url_cliente_existente = 'https://z8cnfhmwyb.execute-api.us-east-1.amazonaws.com/test/get-cliente-existe'
url_crear_cliente_naf = 'https://z8cnfhmwyb.execute-api.us-east-1.amazonaws.com/test/post-cliente-odoo-naf'
url_actualiza_cliente_naf = 'https://z8cnfhmwyb.execute-api.us-east-1.amazonaws.com/test/post-cliente-odoo-naf'

status_code_correct = 200
status_code_error = 400
status_code_cliente_existente = 201

no_error_token = 0
contacto_existe = "si"
contacto_no_existe = "no"


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Cambios'

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
                self.creaar_cliente_naf()
        else:
            _logger.info("Error al realizar petición")

    def existe_cliente_naf(self):
        task = {
            "NO_CIA": "12",
            "GRUPO": "CP",
            "NO_CLIENTE": "CP-002",
        }
        headers = {
            "auth": token
        }
        _logger.info("token: " + token)
        resp = requests.get(url_cliente_existente, params=task, headers=headers)
        # resp = requests.Request('GET', url, data=task, headers=header)
        if resp.status_code == status_code_correct:
            json_respuesta = resp.json()
            _logger.info('json_respuesta: ' + str(json_respuesta))
            if json_respuesta['status_code'] == status_code_correct:
                if json_respuesta['existe'] == contacto_existe:
                    _logger.info("Existe el contacto en sistema Naf")
                elif json_respuesta['existe'] == contacto_no_existe:
                    _logger.info("No existe el contacto en sistema Naf")
            else:
                _logger.info("Error al realizar petición json_respuesta['message']: " + str(json_respuesta['message']))
        else:
            _logger.info("Error al realizar petición resp.status_code: " + str(resp.status_code))

    def creaar_cliente_naf(self):
        task = {
            "tipo_cliente": 2,
            "id_crm": 99888795,
            "nombre": "Pruebas Galet",
            "cedula": "03651784-5",
            "direccion": "El salvador",
            "telefono_fijo": "22222222",
            "telefono_celular": "88888888",
            "email": "prubas@promed-sa.com",
            "lugar_trabajo": "San salvador",
            "direccion_trabajo": "direccion",
            "email_trabajo": "pruebas@email.com",
            "nombre_establecimiento": "Pruebas Galet",
            "razon_social": "",
            "ruc": "15484414",
            "direccion_comercial": "El salvador",
            "estado": 2,
            "no_cia": "01",
            "codigo_vendedor": "SM62",
            "digito_verificador": "DV",
            "contacto": "contactos",
            "ciudad": "San salvador",
            "provincia": "San salvador",
            "pais": "El salvador",
            "pagina_web": "www.pruebas.com"
        }
        headers = {
            "auth": token
        }
        _logger.info("creaar_cliente_naf() token: " + token)
        resp = requests.post(url_crear_cliente_naf, data=task, headers=headers)
        if resp.status_code == status_code_correct:
            json_respuesta = resp.json()
            _logger.info(json_respuesta)
            if json_respuesta['status_code'] == status_code_correct:
                _logger.info("Cliente creado correctamente, mensaje: " + str(json_respuesta['message']))

            elif json_respuesta['status_code'] == status_code_cliente_existente:
                _logger.info("Cliente ya existe, mensaje: " + str(json_respuesta['message']))

            elif json_respuesta['status_code'] == status_code_error:
                _logger.info("Error al crear cliente, mensaje: " + str(json_respuesta['message']))

        else:
            _logger.info("Error al realizar petición resp.status_code: " + str(resp.status_code))
