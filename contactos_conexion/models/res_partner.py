from odoo import models, fields, api,_
import logging, ast

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = 'res.partner'

    codigo_naf = fields.Char(
        string="Código Naf",
        store=True
    )
    tipo = fields.Char(
        string="Tipo",
        store=True
    )
    cedula = fields.Char(
        string="Cedula",
        store=True
    )
    estado = fields.Selection(
        selection=[('1', 'Sin código NAF'), ('2', 'En proceso NAF'), ('3', 'Asignado código NAF')],
        string="estado código NAF",
        store=True
    )
    digito_verificador = fields.Char(
        string="Dígito verificador",
        store=True
    )
    no_cia = fields.Char(
        string="No Cia",
        store=True
    )
    grupo = fields.Char(
        string="Grupo",
        store=True
    )
    no_cliente = fields.Char(
        string="No cliente",
        store=True
    )
    limite_credito = fields.Float(
        string="Límite de crédito",
        default=0,
        store=True
    )
    saldo = fields.Float(
        string="Saldo",
        default=0,
        store=True
    )
