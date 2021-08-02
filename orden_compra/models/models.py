# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Factura(models.Model):
	_inherit='account.move'




class LinesFactura(models.Model):
	_inherit='account.move.line'
	costo=fields.Float(related='product_id.standard_price')
	precio=fields.Float(related='product_id.lst_price')






class Almacen(models.Model):
	_inherit='stock.warehouse'
	auto_recepcion=fields.Boolean()
	stock_visible=fields.Boolean()


class Company(models.Model):
	_inherit='res.company'
	order_compra=fields.Boolean()