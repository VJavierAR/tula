# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import logging, ast
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError
from statistics import mean

class Product(models.Model):
	_inherit='product.product'

	@api.onchange('standard_price', 'x_studio_utilidad_precio_de_venta')
	@api.depends_context('force_company')
	def cambio_precio_de_venta(self):
		company = self.env.context.get('force_company', False)
		for rec in self:
			if(rec.with_context(force_company=self.env.company.id).nuevo_costo_facturacion_impuesto==0):
				if rec.with_context(force_company=self.env.company.id).standard_price and rec.with_context(force_company=self.env.company.id).x_studio_utilidad_precio_de_venta:
					rec.list_price = (rec.with_context(force_company=self.env.company.id).standard_price * rec.with_context(force_company=self.env.company.id).x_studio_utilidad_precio_de_venta / 100) + rec.with_context(force_company=self.env.company.id).standard_price



	# @api.depends('standard_price')
	# def updateCost(self):
	# 	for record in self:
	# 		record.nuevo_costo_facturacion_impuesto=0
	# 		if(record.id):
	# 			f=self.env['account.move.line'].search([['credit','=',0],['parent_state','=','posted'],['product_id','=',record.id]],order='date desc',limit=1)
	# 			record.nuevo_costo_facturacion=f.price_unit
	# 			record.nuevo_costo_facturacion_impuesto=f.price_unit+f.impuesto









class ProductTemplate(models.Model):
	_inherit='product.template'
	#nuevo_costo_facturacion=fields.Float(default=0,string='Precio Compra',company_dependent=True,check_company=True)
	#nuevo_costo_facturacion_impuesto=fields.Float(default=0,string='Precio Venta+impuesto',company_dependent=True,check_company=True)

	# @api.depends('standard_price')
	# def updateCost(self):
	# 	for record in self:
	# 		record.nuevo_costo_facturacion=0
	# 		if(record.id):
	# 			a=[]
	# 			b=[]
	# 			for f in record.product_variant_ids:
	# 				c=f.nuevo_costo_facturacion if(f.nuevo_costo_facturacion!=0) else f.lst_price
	# 				d=f.nuevo_costo_facturacion_impuesto if(f.nuevo_costo_facturacion_impuesto!=0) else f.lst_price
	# 				a.append(c)
	# 				b.append(d)
	# 			record.nuevo_costo_facturacion=mean(a)
	# 			record.nuevo_costo_facturacion_impuesto=mean(b)