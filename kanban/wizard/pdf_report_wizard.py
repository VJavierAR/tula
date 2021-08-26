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
    _name = 'pdf.report.requisito.compra'
    _description = 'Vista previa de reporte PDF'

    requisito_compra_id = fields.Integer(
        string="Requisito de compra id",
    )
    pdfReporte = fields.Binary(
        string="PDF",
        store=True
    )

    def imprimir(self):
        orden = self.env['requisito.compra'].search([
            ('id', '=', self.requisito_compra_id)
        ])
        data = {
            'model': 'requisito.compra',
            'form': orden.read()[0]
        }
        return self.env.ref('kanban.reporte_de_requisito_de_compra').report_action(orden)
