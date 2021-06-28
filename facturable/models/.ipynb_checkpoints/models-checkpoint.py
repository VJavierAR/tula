#-*- coding: utf-8 -*-

from odoo import models, fields, api
import logging, ast
_logger = logging.getLogger(__name__)

class fact(models.Model):
    _inherit = 'sale.order.line'
    facturable=fields.Float('Facturable',compute='f')
    facturablePrevio=fields.Float('Facturable Previo')
    @api.depends('qty_delivered')
    def f(self):
        _logger.info('Hola')
        valor=1
        for record in self:
            if(record.qty_delivered==record.product_uom_qty):
                valor=0
            if(record.qty_delivered!=record.product_uom_qty):
                q=self.env['stock.move'].search([['sale_line_id','=',record.id]])
                hechos=q.filtered(lambda x:x.state=='done' and x.location_id.id==record.warehouse_id.lot_stock_id.id)
                cancelados=q.filtered(lambda x:x.state=='cancel' and x.location_id.id==record.warehouse_id.lot_stock_id.id)
                otros=q.filtered(lambda x:x.state not in ['cancel','done'] and x.location_id.id==record.warehouse_id.lot_stock_id.id)
                if(len(cancelados)>0):
                    valor=0
                else:
                    valor=record.product_uom_qty-record.qty_delivered
        self.facturable=valor
        
class facturable(models.Model):
    _inherit = 'purchase.order.line'
    facturable=fields.Float('Facturable',compute='full')
    
    @api.depends('qty_received')
    def full(self):
        for record in self:
            q=self.env['stock.move'].search([['product_id','=',record.product_id.id],['sale_line_id','!=',False]],order='date asc')
            fin=q.filtered(lambda x:x.state not in ['done','cancel'])
            _logger.info(record.qty_received)
            _logger.info(len(fin))
            valor=record.qty_received
            for f in fin:
                if(valor>0):
                    temp=valor
                    valor=valor-record.product_uom_qty
                    _logger.info(f.sale_line_id.id)
                    if(valor>=0):
                        f.sale_line_id.write({'facturablePrevio':record.product_uom_qty})
                    else:
                        f.sale_line_id.write({'facturablePrevio':temp})
        self.facturable=0