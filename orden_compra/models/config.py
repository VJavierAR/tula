# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import logging, ast
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError
from statistics import mean



class AlertaDescuento(models.TransientModel):
	_name = 'purchase.order.alerta'
	_description = 'Alerta'

	mensaje = fields.Text(string='Mensaje')

class Almacen(models.Model):
	_inherit='stock.warehouse'
	auto_recepcion=fields.Boolean()
	stock_visible=fields.Boolean()


class Company(models.Model):
	_inherit='res.company'
	orden_compra=fields.Boolean()
	price_lst=fields.Boolean()