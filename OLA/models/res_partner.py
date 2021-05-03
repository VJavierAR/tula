from odoo import models, fields, api,_
import logging, ast

_logger = logging.getLogger(__name__)

class partner(models.Model):
    _inherit = 'res.partner'

    limite_credito = fields.Integer(
        string="Límite de crédito",
        company_dependent=True,
        check_company=True
    )

    limite_credito_conglomerado = fields.Integer(
        string="Límite de crédito conglomerado",
        company_dependent=False,
        check_company=False
    )

    correoFac = fields.Char(
        string = "Correo Facturacion"
    )
    
    correoCobranza = fields.Char(
        string = "Correo Cobranza"
    )
    



    limite_credito_sucursal = fields.Monetary(
        string = "Límite de crédito de sucursal"
    )