from odoo import models, fields, api, _

class SaleLine(models.Model):
    _inherit = "sale.order.line"

    def get_sale_order_line_multiline_description_sale(self, product):
        super(SaleLine, self).get_sale_order_line_multiline_description_sale(product)
        return product.description_sale or product.name

