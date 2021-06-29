#-*- coding: utf-8 -*-

from odoo import models, fields, api
import logging, ast
_logger = logging.getLogger(__name__)

class fact(models.Model):
    _inherit = 'sale.order.line'
    facturable=fields.Float('Facturable',compute='f')
    facturablePrevio=fields.Float('Facturable Previo')
    arreglo=fields.Char(default='[]')

    @api.depends('qty_delivered','product_uom_qty')
    def f(self):
        _logger.info('Hola')
        valor=1
        for record in self:
            if(record.qty_delivered==record.product_uom_qty):
                valor=0
            if(record.qty_delivered!=record.product_uom_qty):
                q=self.env['stock.move'].search([['sale_line_id','=',record.id]])
                _logger.info(len(q))
                hechos=q.filtered(lambda x:x.state=='done')
                #_logger.info(len(otros))
                cancelados=q.filtered(lambda x:x.state=='cancel')
                otros=q.filtered(lambda x:x.state not in ['cancel','done'])
                _logger.info(len(cancelados))
                if(len(cancelados)>0):
                    valor=0
                else:
                    espera=q.filtered(lambda x:x.state not in ['assigned','partially_available','cancel','done'])
                    asigados=q.filtered(lambda x:x.state in ['assigned','partially_available'])
                    _logger.info(len(asigados))
                    _logger.info(len(espera))
                    #valor=record.product_uom_qty-record.qty_delivered
                    valor=sum(asigados.mapped('reserved_availability')) if(len(asigados)>0) else record.product_uom_qty-record.qty_delivered
            record.facturable=valor
        
        

class facturable(models.Model):
    _inherit = 'purchase.order.line'
    facturable=fields.Float('Facturable',compute='full',default=0)
    
    @api.depends('qty_received')
    def full(self):
        for record in self:
            q=self.env['stock.move'].search([['product_id','=',record.product_id.id],['sale_line_id','!=',False]],order='date asc')
            fin=q.filtered(lambda x:x.state not in ['done','cancel','asigned'])
            _logger.info(record.qty_received)
            _logger.info(len(fin))
            valor=record.qty_received if(record.facturable==0) else record.facturable
            for f in fin:
                arr=eval(f.sale_line_id.arreglo)
                if(self.id not in arr):
                    if(valor>0):
                        temp=valor
                        valor=valor-record.product_uom_qty
                        if(valor>=0):
                            f.sale_line_id.write({'facturablePrevio':record.product_uom_qty,'arreglo':str(arr.append(record.id))})
                        else:
                            f.sale_line_id.write({'facturablePrevio':temp,'arreglo':str(arr.append(record.id))})
        self.facturable=valor