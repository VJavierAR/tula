# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging, ast
_logger = logging.getLogger(__name__)
import datetime

class report(models.AbstractModel):
    _name = 'report.report_custom_template'
    #orden=fields.Many2many('sale.order')
    
    # def _get_picking(self):
    #     ordenes=self.env['stock.picking'].browse(self.env.context.get('active_ids'))
    #     #_logger.info("concentrado 1111")
    #     dato=self.env['ir.sequence'].next_by_code('concentrado')
    #     for pic in self._get_picking():
    #         _logger.info("estado:"+str(pic.state)) 
    #         if(pic.state=='done'):
    #             ot=self.env['stock.picking'].search([['origin','=',pic.origin]])
    #             for t in ot:
    #                 t.write({'concentrado':dato})        
    #                 _logger.info("concentrado:"+str(dato))  
    #     return ordenes
    # @api.multi
    # def concentrado(self,datos):
    #     origen=''
    #     dato=''
    #     for s in datos:
    #         origen=s.origin
    #     ot=self.env['stock.picking'].search([['origin','=',origen]])
    #     if(len(ot)>0):
    #         dato=self.env['ir.sequence'].next_by_code('concentrado')
    #         for o in ot:
    #             o.write({'concentrado':str(dato)})
    #     return str(dato)

    
    # @api.multi
    # def render_html(self, docids, data=None):
    #     report_obj = self.env['report']
    #     report = report_obj._get_report_from_name('module.report_name')
    #     _logger.info("concentrado:")  
    #     dato=self.env['ir.sequence'].next_by_code('concentrado')
    #     for pic in self._get_picking():
    #         _logger.info("estado:"+str(pic.state)) 
    #         if(pic.state=='done'):
    #             ot=self.env['stock.picking'].search([['origin','=',pic.origin]])
    #             for t in ot:
    #                 t.write({'concentrado':dato})        
    #                 _logger.info("concentrado:"+str(dato))  
    #     docargs = {
    #         'doc_ids': docids,
    #         'doc_model': report.model,
    #         'docs': self._get_picking(),
    #     }
    #     return report_obj.render('module.report_name', docargs)
