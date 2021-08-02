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


class SaleOrderOrdenAbierta(models.Model):
    _inherit = 'sale.order'
    _description = 'Orden abierta'

    es_orden_abierta = fields.Boolean(
        string="¿Es odern abierta?"
    )
    """
    reservas = fields.One2many(
        comodel_name='sale.order.reservas',
        inverse_name='sale_id',
        string='Reservas'
    )
    """

    def conf(self):
        orden_abierta = self.es_orden_abierta
        conteo_lineas_confirmadas = 0
        if orden_abierta:
            sale_directa = self.env['sale.order'].create({
                'partner_id': self.partner_id.id,
                'company_id': self.company_id.id,
                'picking_policy': self.picking_policy,
                'date_order': self.date_order,
                'payment_term_id': self.payment_term_id.id
            })
            id_sale_directa = sale_directa.id
            for line in self.order_line:
                if (line.confirma_venta_directa or not line.fecha_programada) and not line.linea_confirmada:
                    linea_generada = line.dup_line_to_order(order_id=id_sale_directa)
                    line.linea_confirmada = True
                    linea_generada.linea_confirmada = True
                if line.linea_confirmada:
                    conteo_lineas_confirmadas += 1
            if conteo_lineas_confirmadas == len(self.order_line.ids):
                self.state = 'sale'
            if len(sale_directa.order_line) == 0:
                sale_directa.unlink()
                display_msg = "No se genero orden directa al no tener lineas que confirmar"
                self.message_post(body=display_msg)
            else:
                display_msg = "Se genero orden directa con las líneas: <br/>Orden generada: " + sale_directa.name
                self.message_post(body=display_msg)
                sale_directa.action_confirm()
        else:
            self.action_confirm()

    @api.onchange('order_line')
    def cambian_lineas(self):
        if self.order_line:
            for linea in self.order_line:
                if linea.fecha_programada:
                    self.es_orden_abierta = True
                    break

    def cron_orden_abierta(self):
        genero_html = False
        today_date = datetime.today().strftime("%Y-%m-%d")
        today_date = '2021-08-01'
        _logger.info('today_date: ' + str(today_date))
        usuarios_a_notificar = self.env['res.groups'].sudo().search(
            [("name", "=", "Notificaciones de ordenes abiertas")]).mapped('users.id')
        usuarios_a_notificar_correo = self.env['res.groups'].sudo().search(
            [("name", "=", "Notificaciones de ordenes abiertas")]).mapped('users.email')
        estados_no_aprobados = ['draft', 'sent']
        pedidos_de_venta = self.search([
            ('state', 'in', estados_no_aprobados),
            ('es_orden_abierta', '=', True),
        ])

        company_email = ""
        html = "Ordenes abiertas para ser entregadas hoy: "
        for pedido_abierto in pedidos_de_venta:
            company_email = pedido_abierto.company_id.email
            for linea in pedido_abierto.order_line:
                _logger.info("linea.fecha_programada: " + str(linea.fecha_programada) + " today_date: " + str(today_date) + "pedido_abierto: " + pedido_abierto.name)
                if str(linea.fecha_programada) == str(today_date):
                    html += pedido_abierto.name + "<br/>"
                    genero_html = True

        if genero_html:
            _logger.info("listoooooooooooo")
            template_correo = self.env.ref('orden_abierta.notify_orden_abierta_email_template')
            mail = template_correo.generate_email(self.id)
            mail['email_to'] = str(usuarios_a_notificar_correo).replace('[', '').replace(']', '').replace('\'', '')
            mail['body_html'] = html
            mail['email_from'] = company_email
            self.env['mail.mail'].create(mail).send()
