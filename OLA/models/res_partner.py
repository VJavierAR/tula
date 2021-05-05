from odoo import models, fields, api,_
import logging, ast

_logger = logging.getLogger(__name__)

class partner(models.Model):
    _inherit = 'res.partner'

    limite_credito = fields.Integer(
        string="Límite de crédito",
        company_dependent=True,
        check_company=True
    )

    limite_credito_conglomerado = fields.Integer(
        string="Límite de crédito conglomerado",
        company_dependent=False,
        check_company=False
    )

    correoFac = fields.Char(
        string = "Correo Facturacion"
    )
    
    correoCobranza = fields.Char(
        string = "Correo Cobranza"
    )
    


    numeroDeposito = fields.Char(
        string = "Número de deposito"
    )
    
    numeroUnico = fields.Boolean(
        string = "Número Unico"
    )
    

    #${object.partner_id.correoFac},${object.partner_id.email},${object.partner_id.child_ids[0].email}

    limite_credito_sucursal = fields.Monetary(
        string = "Límite de crédito de sucursal"
    )

class Pago(models.Model):
    _inherit = 'account.payment'
    
    
    descripcion = fields.Char(
        string = "Descripción"
    )
    
    
    deposito = fields.Char(
        string = "Deposito"
    )
    
        
    @api.onchange('partner_id')
    def asocia(self):        
        if self.partner_id.numeroUnico:
           self.deposito= self.partner_id.numeroDeposito
    
    
    @api.onchange('deposito')
    def cehckDepositi(self):
        
        if not self.partner_id.numeroUnico and self.deposito :           
           depo=self.env['account.payment'] .search([('deposito','=',self.deposito)])
           if len(depo)>0:
              self.deposito=False
              return {'value':{},'warning':{'title':'warning','message':'Valor ya ocupado'}}
              
class Lineas(models.Model):
    _inherit = 'sale.order.line'            
            
    existencias = fields.Char()
    
    @api.onchange('product_id')
    def buscaProductos(self):                                        
        ft=''
        cabecera='<table><tr><th>Compañia</th><th>Cantidad</th></tr>'
        producto=self.product_id.name
        depo=self.env['product.template'] .search([('name','=',producto)])
        
        for cal in depo:   
            ft='<tr><td>'+cal.company_id.name+'</td><td>'+str(cal.qty_available)+'</td></tr>'+ft
         #self.cal=y
        tabla=cabecera+ft+'</table>'
        
        self.existencias=str(tabla)
    