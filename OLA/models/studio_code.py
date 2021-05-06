from odoo import models, fields, api,_
import datetime, time
from odoo import exceptions
from odoo.exceptions import AccessDenied
import logging, ast
_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
	_inherit='sale.order.line'

	x_studio_field_7lzG1 = fields.Many2one(
		comodel_name='stock.inventory',
		#ondelete='restrict',
		string='Inventario',
		store=True,
		#copy=True,
		#required=False,
		#track_visibility='onchange'
	)

	x_studio_field_GF5gd = fields.Many2one(
		comodel_name='stock.warehouse',
		#ondelete='restrict',
		string='Almacén',
		store=True,
		#copy=True,
		#required=False,
		#track_visibility='onchange'
	)

	x_studio_field_JvgvZ = fields.Many2one(
		comodel_name='res.company',
		#ondelete='restrict',
		string='Compañías',
		store=True,
		#copy=True,
		#required=False,
		#track_visibility='onchange'
	)

	x_studio_field_U1p5V = fields.Many2one(
		comodel_name='stock.warehouse',
		#ondelete='restrict',
		string='Almacén',
		store=True,
		#copy=True,
		#required=False,
		#track_visibility='onchange'
	)

	x_studio_field_pUimo = fields.Many2one(
		comodel_name='stock.location',
		#ondelete='restrict',
		string='Ubicaciones de inventario',
		store=True,
		#copy=True,
		#required=False,
		#track_visibility='onchange'
	)

	x_studio_field_wWTkZ = fields.Many2one(
		comodel_name='report.stock.quantity',
		#ondelete='restrict',
		string='Informe de cantidad de stock',
		store=True,
		#copy=True,
		#required=False,
		#track_visibility='onchange'
	)
	
	"""
	x_studio_field_HNW2r = fields.One2many(
		comodel_name='stock.move',
		inverse_name='sale_line_id',
		string='New UnoAMuchos',
		store=True
	)
	"""

class SaleOrder(models.Model):
	_inherit='sale.order'

	x_studio_field_DtjtD = fields.Many2one(
		comodel_name='sale.order.line',
		#ondelete='restrict',
		string='Línea de pedido de venta',
		store=True,
		#copy=True,
		#required=False,
		#track_visibility='onchange'
	)

	x_studio_field_taP05 = fields.Many2one(
		comodel_name='product.product',
		#ondelete='restrict',
		string='Producto',
		store=True,
		#copy=True,
		#required=False,
		#track_visibility='onchange'
	)
