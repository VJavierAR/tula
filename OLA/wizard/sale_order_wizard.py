# -*- coding: utf-8 -*-
from odoo import fields, models, api,_
from odoo.exceptions import exceptions, UserError
import logging, ast
_logger = logging.getLogger(__name__)


class Alerta_limite_de_credito(models.TransientModel):
    _name = 'sale.order.alerta.limite.credito'
    _description = 'Alerta para el límite de crédito'

    sale_id = fields.Many2one(
        comodel_name = 'sale.order',
        string = 'Pedido de venta relacionado'
    )
    mensaje = fields.Text(
        string = 'Mensaje'
    )

    def confirmar_sale(self):
        _logger.info("Confirmando...")


