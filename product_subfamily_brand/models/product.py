# -*- coding: utf-8 -*-
from odoo import models, fields


class ProductSubfamily(models.Model):
    _name = "product.subfamily"
    _description = "Subfamilia de producto"

    name = fields.Char(string='Nombre', required=True)


class ProductBrand(models.Model):
    _name = "product.brand"
    _description = "Marca de producto"

    name = fields.Char(string='Nombre', required=True)


class ProductSupplier(models.Model):
    _name = "product.supplier"
    _description = "Proveedor de producto"

    name = fields.Char(string='Nombre', required=True)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    subfamily_id = fields.Many2one(comodel_name='product.subfamily', string='Subfamilia', required=False)
    brand_id = fields.Many2one(comodel_name='product.brand', string='Marca', required=False)
    product_supplier_id = fields.Many2one(comodel_name='product.supplier', string='Proveedor', required=False)
