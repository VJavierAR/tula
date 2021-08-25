# -*- coding: utf-8 -*-
from odoo import tools
from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    subfamily_id = fields.Many2one(comodel_name="product.subfamily", string="Subfamilia", required=False)
    brand_id = fields.Many2one(comodel_name="product.brand", string="Marca", required=False)
    product_supplier_id = fields.Many2one(comodel_name="product.supplier", string="Proveedor", required=False)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['subfamily_id'] = ", t.subfamily_id as subfamily_id"
        fields['brand_id'] = ", t.brand_id as brand_id"
        fields['product_supplier_id'] = ", t.product_supplier_id as product_supplier_id"

        groupby += ', t.subfamily_id'
        groupby += ', t.brand_id'
        groupby += ', t.product_supplier_id'

        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
