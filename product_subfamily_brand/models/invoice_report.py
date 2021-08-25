# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    subfamily_id = fields.Many2one(comodel_name="product.subfamily", string="Subfamilia", required=False)
    brand_id = fields.Many2one(comodel_name="product.brand", string="Marca", required=False)
    product_supplier_id = fields.Many2one(comodel_name="product.supplier", string="Proveedor", required=False)


    def _select(self):
        return super(AccountInvoiceReport, self)._select() + ", template.subfamily_id as subfamily_id, template.brand_id as brand_id, template.product_supplier_id as product_supplier_id"

    def _group_by(self):
        return super(AccountInvoiceReport, self)._group_by() + ", template.subfamily_id, template.brand_id, template.product_supplier_id"
