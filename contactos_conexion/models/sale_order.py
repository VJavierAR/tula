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
import json


_logger = logging.getLogger(__name__)

token = ""
username_login = "apiodoo@promed-sa.com"
password_login = "ApiOdoo*001"
url_login = 'https://trxk539p2e.execute-api.us-east-1.amazonaws.com/prueba/Login'
url_cliente_existente = 'https://z8cnfhmwyb.execute-api.us-east-1.amazonaws.com/test/get-cliente-existe'
url_crear_cliente_naf = 'https://z8cnfhmwyb.execute-api.us-east-1.amazonaws.com/test/post-cliente-odoo-naf'
url_actualiza_cliente_naf = 'https://z8cnfhmwyb.execute-api.us-east-1.amazonaws.com/test/put-cliente-odoo-naf'
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

    meta_facturacion_equipo = fields.Float(
        string="Meta de facturación equipo de ventas",
        store=True,
        related="team_id.invoiced_target"
    )

    meta_facturacion_vendedor = fields.Float(
        string="Meta de facturación comercial",
        store=True,
        related="user_id.meta_facturacion"
    )

    def action_confirm_validacion(self):
        # Si proviene de una oportunidad
        if self.opportunity_id.id:
            task_existe_cliente = {
                "NO_CIA": self.partner_id.no_cia or "",
                "GRUPO": self.partner_id.grupo or "",
                "NO_CLIENTE": self.partner_id.no_cliente or ""
            }
            # Si el cliente no tiene codigo naf
            if self.partner_id.id and not self.partner_id.codigo_naf:
                # si el plazo de pago es de contado
                if self.payment_term_id.id and self.payment_term_id.id == 1:
                    # Verifica si existe cliente en NAF

                    resp = self.existe_cliente_naf(task=task_existe_cliente)
                    _logger.info("resp: " + str(resp))
                    # Si no existe el cliente en NAF entonces, crealo
                    if 'existe' in resp and resp['existe'] == 'no':
                        _logger.info("")
                        company_id = self.env.company.id

                        task = {
                            "tipo_cliente": self.partner_id.tipo or "",
                            "id_crm": self.partner_id.id or "",
                            "nombre": self.partner_id.name or "",
                            "cedula": self.partner_id.cedula or "",
                            "direccion": self.opportunity_id.street or "asdasd",
                            "telefono_fijo": self.opportunity_id.phone or "",
                            "telefono_celular": self.opportunity_id.mobile or "",
                            "email": self.opportunity_id.email_from or "",
                            "lugar_trabajo": self.opportunity_id.lugar_trabajo or "",
                            "direccion_trabajo": self.opportunity_id.street or "",
                            "email_trabajo": self.opportunity_id.email_from or "",
                            "nombre_establecimiento": self.opportunity_id.nombre_establecimiento or "",
                            "razon_social": self.opportunity_id.razon_social or None,
                            "ruc": self.partner_id.vat or "",
                            "direccion_comercial": self.opportunity_id.direccion_comercial or "",
                            "estado": int(self.partner_id.estado),
                            "no_cia": self.partner_id.no_cia or "",
                            "codigo_vendedor": self.opportunity_id.user_id.codigo_vendedor or "",
                            "digito_verificador": self.partner_id.digito_verificador or "",
                            "contacto": self.opportunity_id.contact_name or "",
                            "ciudad": self.opportunity_id.city or "",
                            "provincia": self.opportunity_id.city or "",
                            "pais": self.opportunity_id.country_id.name or "",
                            "pagina_web": self.opportunity_id.website.split("//")[-1]
                        }
                        _logger.info("task crear_cliente_naf(): \n" + str(task))
                        self.conect()
                        resultado_al_crear = self.crear_cliente_naf(task=task)
                        # Si al crear cliente en NAF, el sistema responde que existe entonces, informa en chatter
                        if 'existe' in resultado_al_crear:
                            _logger.info("Ya existe e cliente actualizalo")
                            display_msg = "Se intento crear cliente en NAF pero este ya existe"
                            self.message_post(body=display_msg)
                        # Si se creo exitosamente entonces, informa
                        elif 'creado' in resultado_al_crear:
                            display_msg = "Cliente creado en sistema NAF."
                            self.message_post(body=display_msg)
                        # Si se produjo un error al crear el cliente en NAF entonces, informa
                        elif 'error' in resultado_al_crear:
                            display_msg = "Error al crear cliete en NAF <br/>Mensaje: " + str(resultado_al_crear['error'])
                            self.message_post(body=display_msg)
                            _logger.info("Error al crear")
                    # Si el cliente existe entonces, intenta actualizar los datos en NAF
                    elif 'existe' in resp and resp['existe'] == 'si':
                        # Actualizando datos en NAF
                        _logger.info("existe** name y rcu no se cambian")
                        self.conect()
                        task = {
                            "no_cia": self.partner_id.no_cia or "",
                            "grupo": self.partner_id.grupo or "",
                            "no_cliente": self.partner_id.no_cliente or "",
                            "telefono_fijo": self.partner_id.phone or "",
                            "telefono_celular": self.partner_id.mobile or "",
                            "email": self.partner_id.email or "",
                            "contacto": self.partner_id.name or ""
                        }

                        resultado_al_actualizar = self.actualizar_cliente_naf(task=task)
                        # Si fue exitosa la actualización de los datos del cliente entonces,
                        # informalo, intenta actualizar límite de crédito y saldo
                        if 'exito' in resultado_al_actualizar:
                            display_msg = "Se actualizaron datos de cliete en NAF"
                            self.message_post(body=display_msq)
                            task = {
                                "NO_CIA": self.partner_id.no_cia or "",
                                "GRUPO": self.partner_id.grupo or "",
                                "NO_CLIENTE": self.partner_id.no_cliente or ""
                            }
                            self.conect()
                            # Verificando límite de crédito
                            limite_credito_naf = self.limite_de_credito_cliente_naf(task=task)
                            # Si tíene límite de crédito en sistema NAF entonces, actualiza el límite en Odoo e informa
                            if 'limite' in limite_credito_naf:
                                self.partner_id.limite_credito = limite_credito_naf['limite']
                                display_msg = "Se actualizo límite de crédito de cliente"
                                self.message_post(body=display_msg)
                            # Si ocurre un error al actualizar límite de crédito entonces, informalo
                            elif 'error' in limite_credito_naf:
                                display_msg = "Error al actualizar límite de crédito <br/>Mensaje: " + str(limite_credito_naf['error'])
                                self.message_post(body=display_msg)
                            self.conect()
                            # Verificando saldo
                            saldo_naf = self.saldo_de_cliente_naf(task=task)
                            # Si tiene saldo en sistema NAF entonces, actualizalo e informa
                            if 'saldo' in saldo_naf:
                                self.partner_id.saldo = saldo_naf['limite']
                                display_msg = "Se actualizo saldo de cliente"
                                self.message_post(body=display_msg)
                            # Si ocurre un error al actualizar saldo entonces, informalo
                            elif 'error' in saldo_naf:
                                display_msg = "Error al actualizar saldo <br/>Mensaje: " + str(saldo_naf['error'])
                                self.message_post(body=display_msg)

                        # Si ocurrio un error en la actualización de los datos del cliente entonces, informalo
                        elif 'error' in resultado_al_actualizar:
                            display_msg = "Error al actualizar cliete en NAF.<br/>Mensaje: " + str(resultado_al_actualizar['error'])
                            self.message_post(body=display_msg)

                    # Si al buscar cliente en NAF ocurre un error entonces, informalo
                    elif 'error' in resp:
                        _logger.info("error ***** " + str(resp['error']))
                        display_msg = "Error al verificar si existe cliente en NAF.<br/>Error: " + str(resp['error'])
                        self.message_post(body=display_msg)
                # si el cliente no tiene código NAF y el plazo de pago no es de contado entonces verifica si existe el
                # cliente en sistema NAF
                else:
                    self.conect()
                    resp = self.existe_cliente_naf(task=task_existe_cliente)
                    # Si el cliente no existe en sistema NAF entonces, actualiza datos
                    if 'existe' in resp and resp['existe'] == 'no':
                        self.conect()
                        task = {
                            "no_cia": self.partner_id.no_cia or "",
                            "grupo": self.partner_id.grupo or "",
                            "no_cliente": self.partner_id.no_cliente or "",
                            "telefono_fijo": self.partner_id.phone or "",
                            "telefono_celular": self.partner_id.mobile or "",
                            "email": self.partner_id.email or "",
                            "contacto": self.partner_id.name or ""
                        }

                        resultado_al_actualizar = self.actualizar_cliente_naf(task=task)
                        # Si la actualización del cliente en sistema NAF fue exitosa entonces, informalo
                        if 'exito' in resultado_al_actualizar:
                            _logger.info("Cliente actualizado en naf")
                            display_msg = "Se actualizaron datos de cliete en NAF"
                            self.message_post(body=display_msq)
                        # Si la actualización del cliente en sistema NAF no fue exitosa entonces, informalo
                        elif 'error' in resultado_al_actualizar:
                            display_msg = "Error al actualizar cliete en NAF.</br>Mensaje: " + str(resultado_al_actualizar['error'])
                            self.message_post(body=display_msg)
                    # Si el cliente existe en sistema NAF entonces, verifica si este esta activo en Odoo
                    elif 'existe' in resp and resp['existe'] == 'si':

                        # si el cliente esta activo en Odoo entonces, verifica límite de crédito y saldo
                        # para actualizar estos
                        if self.partner_id.active:
                            self.conect()
                            # verificando límite de credito y saldo de cliente
                            task = {
                                "NO_CIA": self.partner_id.no_cia or "",
                                "GRUPO": self.partner_id.grupo or "",
                                "NO_CLIENTE": self.partner_id.no_cliente or ""
                            }
                            limite_de_credito = self.limite_de_credito_cliente_naf(task=task)

                            # Si tiene límite de crédito en sistema NAF entonces, actualiza el límite de crédito en Odoo
                            # y veifica si el monto del pedido de venta es mayor al límite de crédito en sistema NAF que
                            # en cuyo caso genera alerta para informar que la orden esta excediendo el límite de
                            # crédito.
                            # También actualiza del cliente saldo en Odoo con base al salndo en NAF e informa
                            if 'limite' in limite_de_credito:
                                monto_de_orden = self.amount_total
                                if monto_de_orden > limite_de_credito['limite']:
                                    mensaje = "Límite de crédito excedido: \nMonto de orden: " + str(
                                        monto_de_orden) + "\n Límite de crédito: " + str(limite_de_credito['limite'])
                                    display_msg_limite = "Límite de crédito excedido: <br/>Monto de orden: " + str(
                                        monto_de_orden) + "<br/> Límite de crédito: " + str(limite_de_credito['limite'])
                                    self.message_post(body=display_msg_limite)
                                    self.genera_alerta(mensaje=mensaje)
                                self.partner_id.limite_credito = limite_de_credito['limite']
                                display_msg = "Se actualizo límite de crédito de cliente <br/>Límite de crédito: " + \
                                              str(limite_de_credito['limite'])

                                self.conect()
                                saldo_naf = self.saldo_de_cliente_naf(task=task)
                                if 'saldo' in saldo_naf:
                                    self.partner_id.saldo = saldo_naf['saldo']
                                    display_msg = "<br/>Se actualizo límite de crédito de cliente y saldo<br/>" \
                                                   "Límite de crédito: " + str(limite_de_credito['limite']) \
                                                   + "<br/>Saldo: " + str(saldo_naf['saldo'])
                                elif 'error' in saldo_naf:
                                    display_msg = "Error al actualizar saldo <br/>Error: " + str(saldo_naf['error'])
                                    self.message_post(body=display_msg)

                                self.message_post(body=display_msg)

                            # Si ocurre un error al consultar límite de crédito en NAF entonces, informa
                            elif 'error' in limite_de_credito:
                                display_msg = "Error al consultar límite de crédito <br/>Error: " + str(limite_de_credito['error'])
                                self.message_post(body=display_msg)

                        # Si el cliente no esta activo en Odoo entonces, informa y no permitas confirmar
                        else:
                            display_msg = "El cliente no esta activo, por lo que no es posible confirmar"
                            self.message_post(body=display_msg)
                            return False

                    # Si ocurre un error al verificar si existe el cliente en sistema NAF entonces, informa
                    elif 'error' in resp:
                        _logger.info("error ***** " + str(resp['error']))
                        display_msg = "Error al verificar si existe cliente en NAF.<br/>Error: " + str(resp['error'])
                        self.message_post(body=display_msg)

            # Si el cliente tiene código NAF entonces, verifica el plazo de pago
            else:
                # Si el plazo de pago es de contado
                if self.payment_term_id.id and self.payment_term_id.id == 1:
                    _logger.info("validar que el pago no sea en cheque, solo tarjeta y efectivo")

                # Si el plazo de pago no es de contado entonces, verifica si el cliente esta activo en Odoo
                else:
                    # Si el cliente esta activo en Odoo entonces, consulta límite de crédito y saldo de cliente en
                    # sistema NAF para actualizar estos datos
                    if self.partner_id.active:
                        self.conect()
                        # verificando límite de credito y saldo de cliente
                        task = {
                            "NO_CIA": self.partner_id.no_cia or "",
                            "GRUPO": self.partner_id.grupo or "",
                            "NO_CLIENTE": self.partner_id.no_cliente or ""
                        }
                        limite_de_credito = self.limite_de_credito_cliente_naf(task=task)

                        # Si tiene límite de crédito en sistema NAF entonces, actualiza el límite de crédito en Odoo
                        # y veifica si el monto del pedido de venta es mayor al límite de crédito en sistema NAF que
                        # en cuyo caso genera alerta para informar que la orden esta excediendo el límite de
                        # crédito.
                        # También actualiza del cliente saldo en Odoo con base al salndo en NAF e informa
                        if 'limite' in limite_de_credito:
                            monto_de_orden = self.amount_total
                            if monto_de_orden > limite_de_credito['limite']:
                                mensaje = "Límite de crédito excedido: \nMonto de orden: " + str(
                                    monto_de_orden) + "\n Límite de crédito: " + str(limite_de_credito['limite'])
                                display_msg_limite = "Límite de crédito excedido: <br/>Monto de orden: " + str(
                                    monto_de_orden) + "<br/> Límite de crédito: " + str(limite_de_credito['limite'])
                                self.message_post(body=display_msg_limite)
                                self.genera_alerta(mensaje=mensaje)
                            self.partner_id.limite_credito = limite_de_credito['limite']
                            display_msg = "Se actualizo límite de crédito de cliente <br/>Límite de crédito: " + \
                                          str(limite_de_credito['limite'])
                            self.conect()
                            saldo_naf = self.saldo_de_cliente_naf(task=task)
                            if 'saldo' in saldo_naf:
                                self.partner_id.saldo = saldo_naf['saldo']
                                display_msg = "Se actualizo límite de crédito y saldo de cliente<br/>" \
                                               "Límite de crédito: " + str(limite_de_credito['limite']) + \
                                               "<br/>Saldo: " + str(saldo_naf['saldo'])
                            elif 'error' in saldo_naf:
                                display_msg = "Error al consultar límite de crédito <br/>Error: " + str(saldo_naf['error'])
                                self.message_post(body=display_msg)

                            self.message_post(body=display_msg)

                        # Si ocurre un error al consultar límite de crédito en NAF entonces, informa
                        elif 'error' in limite_de_credito:
                            display_msg = "Error al consultar límite de crédito <br/>Error: " + str(limite_de_credito['error'])
                            self.message_post(body=display_msg)

                    # Si el cliente no esta activo informa de esto y no permitas confirmar
                    else:
                        display_msg = "El cliente no esta activo, por lo que no es posible confirmar"
                        self.message_post(body=display_msg)
                        return False

        self.action_confirm()

    def conect(self):
        _logger.info("SaleOrder.conect(self)")
        task = {"username": username_login, "password": password_login}
        resp = requests.post(url_login, json=task)
        if resp.status_code == status_code_correct:
            json_respuesta = resp.json()
            _logger.info(json_respuesta)
            if json_respuesta['error'] == no_error_token:
                global token
                token = json_respuesta['idToken']
                _logger.info(token)
                # self.crear_cliente_naf()
                # self.actualizar_cliente_naf()
                # self.limite_de_credito_cliente_naf()
                # self.existe_cliente_naf()
                # self.saldo_de_cliente_naf()
        else:
            _logger.info("Error al realizar petición")

    def existe_cliente_naf(self, task=None):
        _logger.info("SaleOrder.existe_cliente_naf(self, task=None)")
        """
        task = {
            "NO_CIA": "12",
            "GRUPO": "CP",
            "NO_CLIENTE": "CP-002",
        }
        """
        headers = {
            "auth": token
        }
        _logger.info("token: " + token)
        resp = requests.get(url_cliente_existente, json=task, headers=headers)
        # resp = requests.Request('GET', url, data=task, headers=header)
        _logger.info("resp.status_code: " + str(resp.status_code))
        if resp.status_code == status_code_correct:
            json_respuesta = resp.json()
            _logger.info('json_respuesta: ' + str(json_respuesta))
            if int(json_respuesta['status_code']) == status_code_correct:
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
        _logger.info("SaleOrder.crear_cliente_naf(self, task=None)")
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
            "razon_social": None,
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
        global token
        headers = {
            "auth": token,
        }
        _logger.info("crear_cliente_naf() token: " + token + "\n task: \n\n" + str(task))
        resp = requests.post(url_crear_cliente_naf, json=task, headers=headers)
        _logger.info("resp al crear: " + str(resp))
        # if resp.status_code == status_code_correct:
        json_respuesta = resp.json()
        _logger.info(json_respuesta)
        if int(json_respuesta['status_code']) == status_code_correct:
            _logger.info("Cliente creado correctamente, mensaje: " + str(json_respuesta['message']))
            return {
                'creado': 'si'
            }
        elif int(json_respuesta['status_code']) == status_code_cliente_existente:
            _logger.info("Cliente ya existe, mensaje: " + str(json_respuesta['message']))
            return {
                'existe': 'Ya existe el cliente'
            }
        elif int(json_respuesta['status_code']) == status_code_error:
            _logger.info("Error al crear cliente, mensaje: " + str(json_respuesta['message']))
            return {
                'error': json_respuesta['message']
            }
        else:
            _logger.info("Error al realizar petición resp.status_code: " + str(resp.status_code))
            return {
                'error': json_respuesta['status_code']
            }
        # else:
        #    _logger.info("Error al realizar petición resp.status_code: " + str(resp.status_code))
        #    return {
        #        'error': str(resp.status_code)
        #    }

    def limite_de_credito_cliente_naf(self, task=None):
        _logger.info("SaleOrder.limite_de_credito_cliente_naf(self, task=None)")
        """
        task = {
            "NO_CIA": "12",
            "GRUPO": "CP",
            "NO_CLIENTE": "CP-002"
        }
        """
        headers = {
            "auth": token
        }
        resp = requests.get(url_limite_de_credito_de_cliente, json=task, headers=headers)
        if resp.status_code == status_code_correct or resp.status_code == status_code_cliente_existente or resp.status_code == status_code_error:
            json_respuesta = resp.json()
            _logger.info(json_respuesta)
            if int(json_respuesta['status_code']) == status_code_correct:
                return {
                    'limite': int(json_respuesta['limite'])
                }
            elif int(json_respuesta['status_code']) == status_code_cliente_existente:
                _logger.info("Cliente no existe, mensaje: " + str(json_respuesta['message']))
                return {
                    'error': json_respuesta['message']
                }
            elif int(json_respuesta['status_code']) == status_code_error:
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
        _logger.info("SaleOrder.saldo_de_cliente_naf(self, task=None)")
        """
        task = {
            "NO_CIA": "12",
            "GRUPO": "CP",
            "NO_CLIENTE": "CP-002"
        }
        """
        headers = {
            "auth": token
        }
        resp = requests.get(url_saldo_de_cliente, json=task, headers=headers)
        if resp.status_code == status_code_correct or resp.status_code == status_code_cliente_existente or resp.status_code == status_code_error:
            json_respuesta = resp.json()
            _logger.info(json_respuesta)
            if int(json_respuesta['status_code']) == status_code_correct:
                return {
                    'saldo': float(json_respuesta['saldo'])
                }
            elif int(json_respuesta['status_code']) == status_code_cliente_existente:
                _logger.info("Cliente no existe, mensaje: " + str(json_respuesta['message']))
                return {
                    'error': json_respuesta['message']
                }
            elif int(json_respuesta['status_code']) == status_code_error:
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
        _logger.info("SaleOrder.actualizar_cliente_naf(self, task=None)")
        _logger.info("task: \n\n" + str(task))
        """
        task = {
            "no_cia": "06",
            "grupo": "C",
            "no_cliente": "CB-34",
            "telefono_fijo": "77778",
            "telefono_celular": "77788",
            "email": "pruebas@promed-sa.com",
            "contacto": "contactos"
        }
        """
        headers = {
            "auth": token
        }
        resp = requests.put(url_actualiza_cliente_naf, json=task, headers=headers)
        if resp.status_code == status_code_correct or resp.status_code == status_code_cliente_existente or resp.status_code == status_code_error:
            json_respuesta = resp.json()
            _logger.info(json_respuesta)
            if int(json_respuesta['status_code']) == status_code_correct:
                return {
                    'exito': json_respuesta['message']
                }
            elif int(json_respuesta['status_code']) == status_code_cliente_existente:
                _logger.info("Cliente no existe, mensaje: " + str(json_respuesta['message']))
                return {
                    'error': json_respuesta['message']
                }
            elif int(json_respuesta['status_code']) == status_code_error:
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
        _logger.info("SaleOrder.genera_alerta(self, mensaje=None)")
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