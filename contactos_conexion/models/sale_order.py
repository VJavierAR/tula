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
url_limite_de_credito_de_cliente = 'https://z8cnfhmwyb.execute-api.us-east-1.amazonaws.com/test/get-cliente-limite-cred'
url_saldo_de_cliente = 'https://z8cnfhmwyb.execute-api.us-east-1.amazonaws.com/test/get-cliente-saldo'

status_code_correct = 200
status_code_error = 400
status_code_cliente_existente = 201

no_error_token = 0
contacto_existe = "si"
contacto_no_existe = "no"


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Cambios'

    def action_confirm_validacion(self):
        # si proviene de una oportunidad
        if self.opportunity_id.id:
            # Si el cliente no tiene codigo naf
            if self.partner_id.id and not self.partner_id.codigo_naf:
                # si el plazo de pago es de contado
                if self.payment_term_id.id and self.payment_term_id.id == 1:
                    self.conect()
                    resp = self.existe_cliente_naf()
                    if 'existe' in resp and resp['existe'] == 'no':
                        company_id = self.env.company.id
                        vat = self.env['res.company'].search([['id', '=', company_id]]).vat
                        task = {
                            "tipo_cliente": self.partner_id.tipo or "",
                            "id_crm": self.partner_id.id or "",
                            "nombre": self.partner_id.name or "",
                            "cedula": self.partner_id.cedula or "",
                            "direccion": self.opportunity_id.street or "",
                            "telefono_fijo": self.opportunity_id.phone or "",
                            "telefono_celular": self.opportunity_id.mobile or "",
                            "email": self.opportunity_id.email_from or "",
                            "lugar_trabajo": self.opportunity_id.lugar_trabajo or "",
                            "direccion_trabajo": self.opportunity_id.street or "",
                            "email_trabajo": self.opportunity_id.email_from or "",
                            "nombre_establecimiento": self.opportunity_id.nombre_establecimiento or "",
                            "razon_social": self.opportunity_id.razon_social or "",
                            "ruc": self.partner_id.vat or "",
                            "direccion_comercial": self.opportunity_id.direccion_comercial or "",
                            "estado": 2,
                            "no_cia": vat or "",
                            # "codigo_vendedor": "SM62",
                            # "digito_verificador": "DV",
                            # "contacto": "contactos",
                            # "ciudad": "San salvador",
                            # "provincia": "San salvador",
                            # "pais": "El salvador",
                            # "pagina_web": "www.pruebas.com"
                        }
                        resultado_al_crear = self.creaar_cliente_naf(task=task)
                        if 'existe' in resultado_al_crear:
                            _logger.info("Ya existe e cliente")
                        elif 'error' in resultado_al_crear:
                            _logger.info("Error al crear")
                    elif 'existe' in resp and resp['existe'] == 'si':
                        _logger.info("existe** ")
                    elif 'error' in resp:
                        _logger.info("error ***** " + str(resp['error']))
                # el plazo de pago no es de contado
                else:
                    self.conect()
                    resp = self.existe_cliente_naf()
                    if 'existe' in resp and resp['existe'] == 'no':
                        company_id = self.env.company.id
                        vat = self.env['res.company'].search([['id', '=', company_id]]).vat
                        task = {
                            "tipo_cliente": self.partner_id.tipo or "",
                            "id_crm": self.partner_id.id or "",
                            "nombre": self.partner_id.name or "",
                            "cedula": self.partner_id.cedula or "",
                            "direccion": self.opportunity_id.street or "",
                            "telefono_fijo": self.opportunity_id.phone or "",
                            "telefono_celular": self.opportunity_id.mobile or "",
                            "email": self.opportunity_id.email_from or "",
                            "lugar_trabajo": self.opportunity_id.lugar_trabajo or "",
                            "direccion_trabajo": self.opportunity_id.street or "",
                            "email_trabajo": self.opportunity_id.email_from or "",
                            "nombre_establecimiento": self.opportunity_id.nombre_establecimiento or "",
                            "razon_social": self.opportunity_id.razon_social or "",
                            "ruc": self.partner_id.vat or "",
                            "direccion_comercial": self.opportunity_id.direccion_comercial or "",
                            "estado": 2,
                            "no_cia": vat or "",
                            # "codigo_vendedor": "SM62",
                            # "digito_verificador": "DV",
                            # "contacto": "contactos",
                            # "ciudad": "San salvador",
                            # "provincia": "San salvador",
                            # "pais": "El salvador",
                            # "pagina_web": "www.pruebas.com"
                        }
                        resultado_al_crear = self.creaar_cliente_naf(task=task)
                        if 'existe' in resultado_al_crear:
                            _logger.info("Ya existe e cliente")
                        elif 'error' in resultado_al_crear:
                            _logger.info("Error al crear")
                    elif 'existe' in resp and resp['existe'] == 'si':
                        _logger.info("existe** ")
                        # verificando límite de credito y saldo de cliente
                        task = {
                            "NO_CIA": "12",
                            "GRUPO": "CP",
                            "NO_CLIENTE": "CP-002"
                        }
                        limite_de_credito = self.limite_de_credito_cliente_naf(task=task)
                        saldo = self.saldo_de_cliente_naf(task=task)
                        monto_de_orden = self.amount_total
                        if monto_de_orden > limite_de_credito:
                            mensaje = "Límite de crédito excedido: \nMonto de orden: " + str(
                                monto_de_orden) + "\n Límite de crédito: " + str(limite_de_credito)
                            self.genera_alerta(mensaje=mensaje)
                    elif 'error' in resp:
                        _logger.info("error ***** " + str(resp['error']))
            # Cliente si tiene codifo naf
            else:
                # si el plazo de pago es de contado
                if self.payment_term_id.id and self.payment_term_id.id == 1:
                    _logger.info("validar que el pago no sea en cheque, solo tarjeta y efectivo")
                # el plazo de pago no es de contado
                else:
                    # verificando límite de credito y saldo de cliente
                    task = {
                        "NO_CIA": "12",
                        "GRUPO": "CP",
                        "NO_CLIENTE": "CP-002"
                    }
                    limite_de_credito = self.limite_de_credito_cliente_naf(task=task)
                    saldo = self.saldo_de_cliente_naf(task=task)
                    monto_de_orden = self.amount_total
                    if monto_de_orden > limite_de_credito:
                        mensaje = "Límite de crédito excedido: \nMonto de orden: " + str(
                            monto_de_orden) + "\n Límite de crédito: " + str(limite_de_credito)
                        self.genera_alerta(mensaje=mensaje)

        self.action_confirm()

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
                    return {
                        'existe': 'si'
                    }
                elif json_respuesta['existe'] == contacto_no_existe:
                    _logger.info("No existe el contacto en sistema Naf")
                    return {
                        'existe': 'no'
                    }
            else:
                _logger.info("Error al realizar petición json_respuesta['message']: " + str(json_respuesta['message']))
                return {
                    'error': json_respuesta['message']
                }
        else:
            _logger.info("Error al realizar petición resp.status_code: " + str(resp.status_code))
            return {
                'error': str(resp.status_code)
            }

    def crear_cliente_naf(self, task=None):
        """
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
        """
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
                return {
                    'creado': 'si'
                }
            elif json_respuesta['status_code'] == status_code_cliente_existente:
                _logger.info("Cliente ya existe, mensaje: " + str(json_respuesta['message']))
                return {
                    'existe': 'Ya existe el cliente'
                }
            elif json_respuesta['status_code'] == status_code_error:
                _logger.info("Error al crear cliente, mensaje: " + str(json_respuesta['message']))
                return {
                    'error': json_respuesta['message']
                }
        else:
            _logger.info("Error al realizar petición resp.status_code: " + str(resp.status_code))
            return {
                'error': str(resp.status_code)
            }

    def limite_de_credito_cliente_naf(self, task=None):
        task = {
            "NO_CIA": "12",
            "GRUPO": "CP",
            "NO_CLIENTE": "CP-002"
        }
        headers = {
            "auth": token
        }
        resp = requests.get(url_crear_cliente_naf, params=task, headers=headers)
        if resp.status_code == status_code_correct:
            json_respuesta = resp.json()
            _logger.info(json_respuesta)
            if json_respuesta['status_code'] == status_code_correct:
                return {
                    'limite': int(json_respuesta['limite'])
                }
            elif json_respuesta['status_code'] == status_code_cliente_existente:
                _logger.info("Cliente no existe, mensaje: " + str(json_respuesta['message']))
                return {
                    'error': json_respuesta['message']
                }
            elif json_respuesta['status_code'] == status_code_error:
                _logger.info("Error al crear cliente, mensaje: " + str(json_respuesta['message']))
                return {
                    'error': json_respuesta['message']
                }
        else:
            _logger.info("Error al realizar petición resp.status_code: " + str(resp.status_code))
            return {
                'error': str(resp.status_code)
            }

    def saldo_de_cliente_naf(self, task=None):
        task = {
            "NO_CIA": "12",
            "GRUPO": "CP",
            "NO_CLIENTE": "CP-002"
        }
        headers = {
            "auth": token
        }
        resp = requests.get(url_crear_cliente_naf, params=task, headers=headers)
        if resp.status_code == status_code_correct:
            json_respuesta = resp.json()
            _logger.info(json_respuesta)
            if json_respuesta['status_code'] == status_code_correct:
                return {
                    'saldo': float(json_respuesta['limite'])
                }
            elif json_respuesta['status_code'] == status_code_cliente_existente:
                _logger.info("Cliente no existe, mensaje: " + str(json_respuesta['message']))
                return {
                    'error': json_respuesta['message']
                }
            elif json_respuesta['status_code'] == status_code_error:
                _logger.info("Error al crear cliente, mensaje: " + str(json_respuesta['message']))
                return {
                    'error': json_respuesta['message']
                }
        else:
            _logger.info("Error al realizar petición resp.status_code: " + str(resp.status_code))
            return {
                'error': str(resp.status_code)
            }

    def actualizar_cliente_naf(self, task=None):
        task = {
            "no_cia": "06",
            "grupo": "C",
            "no_cliente": "CB-34",
            "telefono_fijo": "77778",
            "telefono_celular": "77788",
            "email": "pruebas@promed-sa.com",
            "contacto": "contactos"
        }
        headers = {
            "auth": token
        }
        resp = requests.put(url_actualiza_cliente_naf, data=task, headers=headers)
        if resp.status_code == status_code_correct:
            json_respuesta = resp.json()
            _logger.info(json_respuesta)
            if json_respuesta['status_code'] == status_code_correct:
                return {
                    'exito': json_respuesta['message']
                }
            elif json_respuesta['status_code'] == status_code_cliente_existente:
                _logger.info("Cliente no existe, mensaje: " + str(json_respuesta['message']))
                return {
                    'error': json_respuesta['message']
                }
            elif json_respuesta['status_code'] == status_code_error:
                _logger.info("Error al crear cliente, mensaje: " + str(json_respuesta['message']))
                return {
                    'error': json_respuesta['message']
                }
        else:
            _logger.info("Error al realizar petición resp.status_code: " + str(resp.status_code))
            return {
                'error': str(resp.status_code)
            }

    def genera_alerta(self, mensaje=None):
        view = self.env.ref('contactos_conexion.sale_order_alerta_view')
        wiz = self.env['sale.order.alerta'].create({'mensaje': mensaje})
        return {
            'name': _('Alerta'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sale.order.alerta',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }