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
            _logger.info("codigos_producto: " + str(codigos_producto))
            domain = ['|', '|', '|',
                      ('name', operator, name),
                      ('default_code', operator, name),
                      ('barcode', operator, name),
                      ('id', 'in', codigos_producto)
                      ] + args
        recs = self.search(domain, limit=limit)
        _logger.info("recs: " + str(recs))
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
