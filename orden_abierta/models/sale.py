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
                    line.dup_line_to_order(order_id=id_sale_directa)
                    line.linea_confirmada = True
                if line.linea_confirmada:
                    conteo_lineas_confirmadas += 1
            if conteo_lineas_confirmadas == len(self.order_line.ids):
                self.state = 'sale'
            if len(sale_directa.order_line) == 0:
                sale_directa.unlink()
                display_msg = "No se genero orden directa al no tener lineas que confirmar"
                self.message_post(body=display_msg)
            else:
                display_msg = "Se genero orden directa con las líneas sin fecha programada: <br/>Orden generada: " + sale_directa.name
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
