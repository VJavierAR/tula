#-*- coding: utf-8 -*-

from odoo import models, fields, api,_
import logging, ast
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError

class fact(models.Model):
    _inherit = 'sale.order.line'
    cantidad_facturable=fields.Float('Cantidad Facturable',compute='f')
    facturable=fields.Float('Facturable',default=0)
    arreglo=fields.Char(default='[]')
    check=fields.Boolean()

    @api.depends('qty_invoiced','product_uom_qty','price_unit')
    def f(self):
        valor=0
        for record in self:
            if(record.qty_invoiced==record.product_uom_qty or record.qty_invoiced!=0):
                valor=0
            if(record.qty_invoiced!=record.product_uom_qty and record.product_id.type!='service'):
                q=self.env['stock.move'].search([['sale_line_id','=',record.id],['picking_code','=','outgoing']])
                t=record.product_id.bom_ids.mapped('bom_line_ids.product_id.id')
                e=record.product_id.bom_ids.mapped('bom_line_ids.product_qty')
                if(len(q)>0 and t==[]):
                    hechos=q.filtered(lambda x:x.state=='done')
                    cancelados=q.filtered(lambda x:x.state=='cancel')
                    otros=q.filtered(lambda x:x.state not in ['cancel','done'])
                    espera=q.filtered(lambda x:x.state not in ['assigned','partially_available','cancel','done'])
                    asigados=q.filtered(lambda x:x.state in ['assigned','partially_available'])
                    valor=sum(asigados.mapped('reserved_availability')) if(len(asigados)>0) else sum(espera.mapped('reserved_availability'))
                    if(record.product_id.virtual_available>0 and valor==0):
                        t=record.product_id.virtual_available-record.product_uom_qty
                        valor=record.product_uom_qty if(t>=0) else record.product_id.virtual_available
                    #if(record.product_id.virtual_available<0 and valor==0):
                    #    if(record.product_uom_qty--record.product_id.virtual_available>=0):
                    #        valor=record.product_uom_qty--record.product_id.virtual_available
                else:
                    if(record.product_id.virtual_available>0):
                        t=record.product_id.virtual_available-record.product_uom_qty
                        valor=record.product_uom_qty if(t>=0) else record.product_id.virtual_available
                    else:
                        valor=0
            if(record.qty_invoiced!=record.product_uom_qty and record.product_id.type=='service'):
                valor=record.product_uom_qty
            record.cantidad_facturable=valor
            record.facturable=valor*record.price_reduce

    @api.onchange('product_id')
    def changePro(self):
        for record in self:
            if(record.product_id.id):
                if(record.check==True and record.product_id.promocion==False):
                    raise UserError('No se puede agregar el producto dado que no cuenta con promocion')              

class fact(models.Model):
    _inherit = 'sale.order'
    promocion=fields.Boolean('Promocion',store=True)

    @api.onchange('order_line')
    def check(self):
        for o in self.order_line:
            if(o.qty_invoiced==0):
                o.f()

    @api.onchange('invoice_count','invoice_ids')
    def promo(self):
        for record in self:
            if(record.promocion):
                for inv in record.invoice_ids:
                    inv['solicitud']=record.id

    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))
        if(self.delivery_set==False or self.recompute_delivery_price==False):
            raise UserError(_('Faltan costos de envio'))
        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
            'date_order': fields.Datetime.now()
        })

        # Context key 'default_name' is sometimes propagated up to here.
        # We don't need it and it creates issues in the creation of linked records.
        context = self._context.copy()
        context.pop('default_name', None)

        self.with_context(context)._action_confirm()
        if self.env.user.has_group('sale.group_auto_done_setting'):
            self.action_done()
        return True

class facturable(models.Model):
    _inherit = 'purchase.order.line'
    facturable=fields.Float('Facturable',compute='full',default=0)
    @api.depends('qty_received')
    def full(self):
        self.facturable=0
    # @api.depends('qty_received')
    # def full(self):
    #     for record in self:
    #         q=self.env['stock.move'].search([['product_id','=',record.product_id.id],['sale_line_id','!=',False]],order='date asc')
    #         fin=q.filtered(lambda x:x.state not in ['done','cancel','asigned'])
    #         _logger.info(record.qty_received)
    #         _logger.info(len(fin))
    #         valor=record.qty_received if(record.facturable==0) else record.facturable
    #         for f in fin:
    #             arr=eval(f.sale_line_id.arreglo)
    #             if(self.id not in arr):
    #                 if(valor>0):
    #                     temp=valor
    #                     valor=valor-record.product_uom_qty
    #                     if(valor>=0):
    #                         f.sale_line_id.write({'facturablePrevio':record.product_uom_qty,'arreglo':str(arr.append(self.id))})
    #                     else:
    #                         f.sale_line_id.write({'facturablePrevio':temp,'arreglo':str(arr.append(self.id))})
    #         record.facturable=valor



class facturas(models.Model):
    _inherit = 'account.move'
    solicitud=fields.Many2one('sale.order')
    promocion=fields.Boolean(related='solicitud.promocion',string='Promocion',store=True)

    #def buscar(self):
    #    for record in self:
    #        s=self.env['sale.order'].search([['name','=',record.invoice_origin]])
    #        record['solicitud']=s

class fact3(models.Model):
    _inherit = 'account.move.line'


    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        ACCOUNTING_FIELDS = ('debit', 'credit', 'amount_currency')
        BUSINESS_FIELDS = ('price_unit', 'quantity', 'discount', 'tax_ids')

        for vals in vals_list:
            move = self.env['account.move'].browse(vals['move_id'])
            vals.setdefault('company_currency_id', move.company_id.currency_id.id) # important to bypass the ORM limitation where monetary fields are not rounded; more info in the commit message

            if move.is_invoice(include_receipts=True):
                currency = move.currency_id
                partner = self.env['res.partner'].browse(vals.get('partner_id'))
                taxes = self.resolve_2many_commands('tax_ids', vals.get('tax_ids', []), fields=['id'])
                tax_ids = set(tax['id'] for tax in taxes)
                taxes = self.env['account.tax'].browse(tax_ids)

                # Ensure consistency between accounting & business fields.
                # As we can't express such synchronization as computed fields without cycling, we need to do it both
                # in onchange and in create/write. So, if something changed in accounting [resp. business] fields,
                # business [resp. accounting] fields are recomputed.
                if any(vals.get(field) for field in ACCOUNTING_FIELDS):
                    if vals.get('currency_id'):
                        balance = vals.get('amount_currency', 0.0)
                    else:
                        balance = vals.get('debit', 0.0) - vals.get('credit', 0.0)
                    price_subtotal = self._get_price_total_and_subtotal_model(
                        vals.get('price_unit', 0.0),
                        vals.get('quantity', 0.0),
                        vals.get('discount', 0.0),
                        currency,
                        self.env['product.product'].browse(vals.get('product_id')),
                        partner,
                        taxes,
                        move.type,
                    ).get('price_subtotal', 0.0)
                    vals.update(self._get_fields_onchange_balance_model(
                        vals.get('quantity', 0.0),
                        vals.get('discount', 0.0),
                        balance,
                        move.type,
                        currency,
                        taxes,
                        price_subtotal
                    ))
                    vals.update(self._get_price_total_and_subtotal_model(
                        vals.get('price_unit', 0.0),
                        vals.get('quantity', 0.0),
                        vals.get('discount', 0.0),
                        currency,
                        self.env['product.product'].browse(vals.get('product_id')),
                        partner,
                        taxes,
                        move.type,
                    ))
                elif any(vals.get(field) for field in BUSINESS_FIELDS):
                    vals.update(self._get_price_total_and_subtotal_model(
                        vals.get('price_unit', 0.0),
                        vals.get('quantity', 0.0),
                        vals.get('discount', 0.0),
                        currency,
                        self.env['product.product'].browse(vals.get('product_id')),
                        partner,
                        taxes,
                        move.type,
                    ))
                    vals.update(self._get_fields_onchange_subtotal_model(
                        vals['price_subtotal'],
                        move.type,
                        currency,
                        move.company_id,
                        move.date,
                    ))

        lines = super(fact3, self).create(vals_list)

        moves = lines.mapped('move_id')
        if self._context.get('check_move_validity', True):
            moves._check_balanced()
        moves._check_fiscalyear_lock_date()
        lines._check_tax_lock_date()
        for sa in lines.sale_line_ids:
            sa._get_invoice_qty()
            sa.f()
        return lines

class ProductTmplUp(models.Model):
    _inherit='product.template'
    promocion=fields.Boolean('Promocion')

    @api.onchange('product_variant_ids','promocion')
    def chec(self):
        for record in self:
            if(len(record.product_variant_ids)==1):
                if(record.promocion):
                    self.env['product.product'].browse(record.product_variant_ids.ids).write({'promocion':True})



class ProductUp(models.Model):
    _inherit='product.product'
    promocion=fields.Boolean('Promocion')




