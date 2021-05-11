# -*- coding: utf-8 -*-
from odoo import fields, models, api,_
from odoo.exceptions import UserError
from odoo import exceptions
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
        self.sale_id.write(
            {
                'bloqueo_limite_credito': False
            }
        )
        self.sale_id.action_confirm()


class AlertaDescuento(models.TransientModel):
    _name = 'sale.order.alerta.descuento'
    _description = 'Alerta para el descuento'

    mensaje = fields.Text(
        string='Mensaje'
    )