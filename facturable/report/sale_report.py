from odoo import tools
from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"
    # _description = "Sales Analysis Report"
    # _auto = False
    # _rec_name = 'date'
    # _order = 'date desc'

    # @api.model
    # def _get_done_states(self):
    #     return ['sale', 'done', 'paid']

    # name = fields.Char('Order Reference', readonly=True)
    # date = fields.Datetime('Order Date', readonly=True)
    # product_id = fields.Many2one('product.product', 'Product Variant', readonly=True)
    # product_uom = fields.Many2one('uom.uom', 'Unit of Measure', readonly=True)
    # product_uom_qty = fields.Float('Qty Ordered', readonly=True)
    # qty_delivered = fields.Float('Qty Delivered', readonly=True)
    # qty_to_invoice = fields.Float('Qty To Invoice', readonly=True)
    # qty_invoiced = fields.Float('Qty Invoiced', readonly=True)
    # partner_id = fields.Many2one('res.partner', 'Customer', readonly=True)
    # company_id = fields.Many2one('res.company', 'Company', readonly=True)
    # user_id = fields.Many2one('res.users', 'Salesperson', readonly=True)
    # price_total = fields.Float('Total', readonly=True)
    # price_subtotal = fields.Float('Untaxed Total', readonly=True)
    # untaxed_amount_to_invoice = fields.Float('Untaxed Amount To Invoice', readonly=True)
    # untaxed_amount_invoiced = fields.Float('Untaxed Amount Invoiced', readonly=True)
    # product_tmpl_id = fields.Many2one('product.template', 'Product', readonly=True)
    # categ_id = fields.Many2one('product.category', 'Product Category', readonly=True)
    # nbr = fields.Integer('# of Lines', readonly=True)
    # pricelist_id = fields.Many2one('product.pricelist', 'Pricelist', readonly=True)
    # analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', readonly=True)
    # team_id = fields.Many2one('crm.team', 'Sales Team', readonly=True)
    # country_id = fields.Many2one('res.country', 'Customer Country', readonly=True)
    # industry_id = fields.Many2one('res.partner.industry', 'Customer Industry', readonly=True)
    # commercial_partner_id = fields.Many2one('res.partner', 'Customer Entity', readonly=True)
    # state = fields.Selection([
    #     ('draft', 'Draft Quotation'),
    #     ('sent', 'Quotation Sent'),
    #     ('sale', 'Sales Order'),
    #     ('done', 'Sales Done'),
    #     ('cancel', 'Cancelled'),
    #     ], string='Status', readonly=True)
    # weight = fields.Float('Gross Weight', readonly=True)
    # volume = fields.Float('Volume', readonly=True)

    # discount = fields.Float('Discount %', readonly=True)
    # discount_amount = fields.Float('Discount Amount', readonly=True)
    # campaign_id = fields.Many2one('utm.campaign', 'Campaign')
    # medium_id = fields.Many2one('utm.medium', 'Medium')
    # source_id = fields.Many2one('utm.source', 'Source')

    # order_id = fields.Many2one('sale.order', 'Order #', readonly=True)
    facturable = fields.Float('Facturable', readonly=True)
    facturable_facturado = fields.Float('Facturable + Facturado', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['facturable'] = ",sum(l.facturable / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) as facturable"
        fields['facturable_facturado'] = ",sum(l.facturable / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END)+sum(l.untaxed_amount_invoiced / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) as facturable"
        #s=self.env['sale.order.line'].search([['qty_invoiced','!=',0]])
        #for sa in s:
        #    sa.f()
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)

    # def init(self):
    #     # self._table = sale_report
    #     tools.drop_view_if_exists(self.env.cr, self._table)
    #     self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))