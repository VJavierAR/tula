from odoo import models, fields, api,_
import logging, ast

_logger = logging.getLogger(__name__)

class partner(models.Model):
    _inherit = 'res.partner'

    limite_credito = fields.Monetary(
        string = "Límite de crédito"
    )

    correoFac = fields.Char(
        string = "Correo Facturacion"
    )
    
    correoCobranza = fields.Char(
        string = "Correo Cobranza"
    )
    


    numeroDeposito = fields.Char(
        string = "Número de deposito"
    )
    
    numeroUnico = fields.Char(
        string = "Número Unico"
    )
    

    #${object.partner_id.correoFac},${object.partner_id.email},${object.partner_id.child_ids[0].email}

    limite_credito_sucursal = fields.Monetary(
        string = "Límite de crédito de sucursal"
    )