# -*- coding: utf-8 -*-

from odoo import models, fields, api



class RepairLine(models.Model):
    _name = 'repair.product'
    _description = 'Repair Product'
    name = fields.Text('Description', required=True)
    repair_id = fields.Many2one('sale.order', 'Repair Order Reference',index=True, ondelete='cascade')
    type = fields.Selection([('add', 'Add'),('remove', 'Remove')], 'Type', default='add', required=True)
    product_id = fields.Many2one('product.product', 'Product', required=True)
    invoiced = fields.Boolean('Invoiced', copy=False, readonly=True)
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price')
    price_subtotal = fields.Float('Subtotal', compute='_compute_price_subtotal', store=True, digits=0)
    tax_id = fields.Many2many('account.tax', 'repair_operation_line_tax', 'repair_operation_line_id', 'tax_id', 'Taxes')
    product_uom_qty = fields.Float('Quantity', default=1.0,digits='Product Unit of Measure', required=True)
    product_uom = fields.Many2one('uom.uom', 'Product Unit of Measure',required=True, domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    invoice_line_id = fields.Many2one('account.move.line', 'Invoice Line',copy=False, readonly=True)
    location_id = fields.Many2one('stock.location', 'Source Location',index=True, required=True)
    location_dest_id = fields.Many2one('stock.location', 'Dest. Location',index=True, required=True)
    move_id = fields.Many2one('stock.move', 'Inventory Move',copy=False, readonly=True)
    lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial')
    state = fields.Selection([('draft', 'Draft'),('confirmed', 'Confirmed'),('done', 'Done'),('cancel', 'Cancelled')], 'Status', default='draft',copy=False, readonly=True, required=True,help='The status of a repair line is set automatically to the one of the linked repair order.')

    @api.constrains('lot_id', 'product_id')
    def constrain_lot_id(self):
        for line in self.filtered(lambda x: x.product_id.tracking != 'none' and not x.lot_id):
            raise ValidationError(_("Serial number is required for operation line with product '%s'") % (line.product_id.name))

    #@api.depends('price_unit', 'repair_id', 'product_uom_qty', 'product_id', 'repair_id.invoice_method')
    @api.depends('price_unit', 'repair_id', 'product_uom_qty', 'product_id')
    def _compute_price_subtotal(self):
        for line in self:
            taxes = line.tax_id.compute_all(line.price_unit, line.repair_id.pricelist_id.currency_id, line.product_uom_qty, line.product_id, line.repair_id.partner_id)
            line.price_subtotal = taxes['total_excluded']

    @api.onchange('type', 'repair_id')
    def onchange_operation_type(self):
        """ On change of operation type it sets source location, destination location
        and to invoice field.
        @param product: Changed operation type.
        @param guarantee_limit: Guarantee limit of current record.
        @return: Dictionary of values.
        """
        if not self.type:
            self.location_id = False
            self.location_dest_id = False
        elif self.type == 'add':
            self.onchange_product_id()
            args = self.repair_id.company_id and [('company_id', '=', self.repair_id.company_id.id)] or []
            warehouse = self.env['stock.warehouse'].search(args, limit=1)
            self.location_id = warehouse.lot_stock_id
            self.location_dest_id = self.env['stock.location'].search([('usage', '=', 'production')], limit=1).id
        else:
            self.price_unit = 0.0
            self.tax_id = False
            self.location_id = self.env['stock.location'].search([('usage', '=', 'production')], limit=1).id
            self.location_dest_id = self.env['stock.location'].search([('scrap_location', '=', True)], limit=1).id

    @api.onchange('repair_id', 'product_id', 'product_uom_qty')
    def onchange_product_id(self):
        """ On change of product it sets product quantity, tax account, name,
        uom of product, unit price and price subtotal. """
        partner = self.repair_id.partner_id
        pricelist = self.repair_id.pricelist_id
        if not self.product_id or not self.product_uom_qty:
            return
        if self.product_id:
            if partner:
                self.name = self.product_id.with_context(lang=partner.lang).display_name
            else:
                self.name = self.product_id.display_name
            if self.product_id.description_sale:
                if partner:
                    self.name += '\n' + self.product_id.with_context(lang=partner.lang).description_sale
                else:
                    self.name += '\n' + self.product_id.description_sale
            self.product_uom = self.product_id.uom_id.id
        if self.type != 'remove':
            if partner and self.product_id:
                fp = partner.property_account_position_id
                if not fp:
                    # Check automatic detection
                    fp_id = self.env['account.fiscal.position'].get_fiscal_position(partner.id, delivery_id=self.repair_id.address_id.id)
                    fp = self.env['account.fiscal.position'].browse(fp_id)
                taxes = self.product_id.taxes_id.filtered(lambda x: x.company_id == self.repair_id.company_id)
                self.tax_id = fp.map_tax(taxes, self.product_id, partner).ids
            warning = False
            if not pricelist:
                warning = {
                    'title': _('No pricelist found.'),
                    'message':
                        _('You have to select a pricelist in the Repair form !\n Please set one before choosing a product.')}
                return {'warning': warning}
            else:
                self._onchange_product_uom()

    @api.onchange('product_uom')
    def _onchange_product_uom(self):
        partner = self.repair_id.partner_id
        pricelist = self.repair_id.pricelist_id
        if pricelist and self.product_id and self.type != 'remove':
            price = pricelist.get_product_price(self.product_id, self.product_uom_qty, partner, uom_id=self.product_uom.id)
            if price is False:
                warning = {
                    'title': _('No valid pricelist line found.'),
                    'message':
                        _("Couldn't find a pricelist line matching this product and quantity.\nYou have to change either the product, the quantity or the pricelist.")}
                return {'warning': warning}
            else:
                self.price_unit = price


class RepairFee(models.Model):
    _name = 'repair.service'
    _description = 'Reparaciones Services'
    repair_id = fields.Many2one('sale.order', 'Repair Order Reference',index=True, ondelete='cascade', required=True)
    name = fields.Text('Description', index=True, required=True)
    product_id = fields.Many2one('product.product', 'Product')
    product_uom_qty = fields.Float('Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price')
    product_uom = fields.Many2one('uom.uom', 'Product Unit of Measure', required=True, domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    price_subtotal = fields.Float('Subtotal', compute='_compute_price_subtotal', store=True, digits=0)
    tax_id = fields.Many2many('account.tax', 'repair_fee_line_tax', 'repair_fee_line_id', 'tax_id', 'Taxes')
    invoice_line_id = fields.Many2one('account.move.line', 'Invoice Line', copy=False, readonly=True)
    invoiced = fields.Boolean('Invoiced', copy=False, readonly=True)

    @api.depends('price_unit', 'repair_id', 'product_uom_qty', 'product_id')
    def _compute_price_subtotal(self):
        for fee in self:
            taxes = fee.tax_id.compute_all(fee.price_unit, fee.repair_id.pricelist_id.currency_id, fee.product_uom_qty, fee.product_id, fee.repair_id.partner_id)
            fee.price_subtotal = taxes['total_excluded']

    @api.onchange('repair_id', 'product_id', 'product_uom_qty')
    def onchange_product_id(self):
        """ On change of product it sets product quantity, tax account, name,
        uom of product, unit price and price subtotal. """
        if not self.product_id:
            return

        partner = self.repair_id.partner_id
        pricelist = self.repair_id.pricelist_id

        if partner and self.product_id:
            fp = partner.property_account_position_id
            if not fp:
                # Check automatic detection
                fp_id = self.env['account.fiscal.position'].get_fiscal_position(partner.id, delivery_id=self.repair_id.address_id.id)
                fp = self.env['account.fiscal.position'].browse(fp_id)
            taxes = self.product_id.taxes_id.filtered(lambda x: x.company_id == self.repair_id.company_id)
            self.tax_id = fp.map_tax(taxes, self.product_id, partner).ids
        if self.product_id:
            if partner:
                self.name = self.product_id.with_context(lang=partner.lang).display_name
            else:
                self.name = self.product_id.display_name
            self.product_uom = self.product_id.uom_id.id
            if self.product_id.description_sale:
                if partner:
                    self.name += '\n' + self.product_id.with_context(lang=partner.lang).description_sale
                else:
                    self.name += '\n' + self.product_id.description_sale

        warning = False
        if not pricelist:
            warning = {
                'title': _('No pricelist found.'),
                'message':
                    _('You have to select a pricelist in the Repair form !\n Please set one before choosing a product.')}
            return {'warning': warning}
        else:
            self._onchange_product_uom()

    @api.onchange('product_uom')
    def _onchange_product_uom(self):
        partner = self.repair_id.partner_id
        pricelist = self.repair_id.pricelist_id
        if pricelist and self.product_id:
            price = pricelist.get_product_price(self.product_id, self.product_uom_qty, partner, uom_id=self.product_uom.id)
            if price is False:
                warning = {
                    'title': _('No valid pricelist line found.'),
                    'message':
                        _("Couldn't find a pricelist line matching this product and quantity.\nYou have to change either the product, the quantity or the pricelist.")}
                return {'warning': warning}
            else:
                self.price_unit = price

