# -*- coding: utf-8 -*-

from odoo import models, fields, api
from email.utils import formataddr
from odoo.exceptions import UserError, RedirectWarning
from odoo import exceptions, _
import logging, ast
import datetime, time
import pytz
import base64
import requests
import json

_logger = logging.getLogger(__name__)

codigos_buscados_lista = []
codigo_buscado = ""


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    codigos_de_producto = fields.One2many(
        comodel_name='product.codigos',
        inverse_name='producto_id',
        string='Códigos de producto'
    )
    en_transito = fields.Integer(
        string="En tránsito",
        default=0,
        compute="_compute_en_transito"
    )

    cantidad_pedidos = fields.Integer(
        string="Cantidad pedidos",
        default=0,
    )
    cantidad_disponible = fields.Integer(
        string="Cantidad disponible",
        default=0
    )


    @api.depends('virtual_available', 'qty_available')
    def _compute_en_transito(self):
        for rec in self:
            rec.en_transito = rec.virtual_available
            rec.cantidad_pedidos=sum(self.env['pedido.abierto.linea'].search([['product_id','=',rec.id],['linea_confirmada','=',True],['cantidad_restante','!=',0]]).mapped('cantidad_restante'))
            rec.cantidad_disponible=rec.quantity_avaible-rec.cantidad_pedidos-rec.en_transito
    """
    def _compute_cantidad_pedidos(self):
        for rec in self:
            if rec.product_variant_id.id:
                lineas_de_pedido_abierto_sin_confirmar = self.env['sale.order.line'].search([
                    ('pedido_abierto_rel', '!=', False),
                    ('linea_confirmada', '=', False),
                    ('product_id', '=', rec.product_variant_id.id)
                ]).mapped('product_uom_qty')
                _logger.info("\nlineas_de_pedido_abierto_sin_confirmar:\n" + str(lineas_de_pedido_abierto_sin_confirmar))
                if len(lineas_de_pedido_abierto_sin_confirmar) > 0:
                    cantidad_total = 0
                    for cantidad in lineas_de_pedido_abierto_sin_confirmar:
                        cantidad_total += cantidad
                    rec.cantidad_pedidos = cantidad_total

    @api.depends('qty_available')
    def _compute_cantidad_disponible(self):
        for rec in self:
            rec.cantidad_disponible = rec.cantidad_pedidos - rec.qty_available
    """

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            codigos_producto = self.env['product.codigos'].search([])
            codigos_producto = codigos_producto.filtered(
                lambda codigo: name.lower() == codigo.codigo_producto.lower()).mapped('producto_id.id')
            domain = ['|', '|', '|',
                      ('name', operator, name),
                      ('default_code', operator, name),
                      ('barcode', operator, name),
                      ('id', 'in', codigos_producto)
                      ] + args
        recs = self.search(domain, limit=limit)
        return recs.name_get()


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            codigos_producto = self.env['product.codigos'].search([])
            codigos_producto = codigos_producto.filtered(
                lambda codigo: name.lower() == codigo.codigo_producto.lower()).mapped('producto_id.id')
            domain = ['|', '|', '|',
                      ('name', operator, name),
                      ('default_code', operator, name),
                      ('barcode', operator, name),
                      ('id', 'in', codigos_producto)
                      ] + args
        recs = self.search(domain, limit=limit)
        return recs.name_get()


class Codigos(models.Model):
    _name = 'product.codigos'
    _description = 'Lista de codigos para los clientes'

    producto_id = fields.Many2one(
        comodel_name='product.template',
        string='Producto relacionado'
    )
    cliente = fields.Many2one(
        comodel_name='res.partner',
        string='Cliente',
        # track_visibility='onchange'
    )
    codigo_producto = fields.Text(
        string="Código de producto",
        store=True,
        # track_visibility='onchange'
    )
