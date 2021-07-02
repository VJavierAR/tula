#-*- coding: utf-8 -*-

from odoo import models, fields, api
import logging, ast
_logger = logging.getLogger(__name__)

class fact(models.Model):
    _inherit = 'sale.order.line'
    cantidad_facturable=fields.Float('Cantidad Facturable',compute='f')
    facturable=fields.Float('Facturable')
    arreglo=fields.Char(default='[]')
    check=fields.Boolean()

    @api.depends('qty_invoiced','product_uom_qty')
    def f(self):
        valor=0
        for record in self:
            if(record.qty_invoiced==record.product_uom_qty or record.qty_invoiced!=0):
                valor=0
            if(record.qty_invoiced!=record.product_uom_qty):
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
                    if(record.product_id.virtual_available<0 and valor==0):
                        if(record.product_uom_qty--record.product_id.virtual_available>=0):
                            valor=record.product_uom_qty--record.product_id.virtual_available
                else:
                    if(record.product_id.virtual_available>0):
                        t=record.product_id.virtual_available-record.product_uom_qty
                        valor=record.product_uom_qty if(t>=0) else record.product_id.virtual_available
                    else:
                        valor=0
            record.cantidad_facturable=valor
            record.facturable=valor*record.price_reduce
        
        

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