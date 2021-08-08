import ast
import base64
import datetime
import json
import logging
import pytz
import time
from odoo import exceptions, _
from odoo import fields, api
from odoo.exceptions import UserError
from odoo.models import TransientModel

_logger = logging.getLogger(__name__)


class PdfReport(TransientModel):
    _name = 'pdf.report'
    _description = 'Vista previa de reporte PDF'

    sale_id = fields.Integer(
        string="Pedido de venta id"
    )
    pdfReporte = fields.Binary(
        string="PDF",
        store=True
    )

    def imprimir(self):
        orden = self.env['sale.order'].search([
            ('id', '=', self.sale_id)
        ])
        data = {
            'model': 'sale.order',
            'form': orden.read()[0]
        }
        return self.env.ref('orden_abierta.reporte_de_lista_empaques').report_action(orden, data=data)
