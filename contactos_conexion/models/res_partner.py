from odoo import models, fields, api,_
import logging, ast

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = 'res.partner'

    codigo_naf = fields.Char(
        string="Código Naf",
        store=True
    )
    tipo = fields.Integer(
        string="Tipo",
        store=True
    )
    cedula = fields.Char(
        string="Cedula",
        store=True
    )
    estado = fields.Selection(
        selection=[('1', 'Sin código NAF'), ('2', 'En proceso NAF'), ('3', 'Asignado código NAF')],
        string="Estado código NAF",
        store=True
    )
    digito_verificador = fields.Char(
        string="Dígito verificador",
        store=True
    )
    no_cia = fields.Char(
        string="No Cia",
        store=True,
        related="company_id.no_cia"
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
    meta_facturacion = fields.Float(
        string="Meta de facturación",
        store=False,
        compute='_compute_meta_facturacion'
    )
    oprotunidad_origen = fields.Char(
        string="oportunidad origen",
        store=True
    )
    creado_desde_oportunidad = fields.Boolean(
        string="Creado desde oportunidad",
        default=False
    )

    def _compute_meta_facturacion(self):
        for rec in self:
            totales = self.env['sale.order'].search(
                [
                    ('partner_id', '=', rec._origin.id),
                    ('state', '=', 'sale')
                ]
            ).mapped('amount_total')
            suma_totales = 0
            for total in totales:
                suma_totales += total
            rec.meta_facturacion = suma_totales
    def create(self,vals):
        _logger.info(vals)
        super(Partner,self).create(vals)