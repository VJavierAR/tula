from odoo import models, fields, api,_
import logging, ast

_logger = logging.getLogger(__name__)


class Partner(models.Model):
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
    colchon_credito = fields.Integer(
        string="Período de gracia",
        default=0,
        company_dependent=False,
        check_company=False
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        store=True,
        copy=True,
        track_visibility='onchange',
        company_dependent=True,
        check_company=True
    )
    property_payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        store=False,
        copy=False,
        company_dependent=True,
        check_company=True
    )
    property_product_pricelist = fields.Many2one(
        comodel_name='product.pricelist',
        store=False,
        copy=False,
        company_dependent=True,
        check_company=True
    )
    property_supplier_payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        store=False,
        copy=False,
        company_dependent=True,
        check_company=True
    )
    limite_de_descuento = fields.Integer(
        string="Límite de descuento (%)",
        store=True,
        company_dependent=True,
        check_company=True
    )
    
    limite_credito_sucursal = fields.Monetary(
        string = "Límite de crédito de sucursal"
    )