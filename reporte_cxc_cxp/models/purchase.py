from odoo import models, fields, api, _

class PurchaseOrder(models.Model):
    _inherit = "purchase.order.line"

    @api.onchange('product_id')
    def onchange_product_id_description(self):
        if self.product_id:
            self.name = self.product_id.description_sale or self.product_id.name