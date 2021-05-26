# -*- coding: utf-8 -*-
from odoo import fields, models, api,_
from odoo.exceptions import UserError
from odoo import exceptions
import logging, ast
_logger = logging.getLogger(__name__)


class Alerta(models.TransientModel):
    _name = 'sale.order.alerta'
    _description = 'Alerta'

    mensaje = fields.Text(
        string='Mensaje'
    )