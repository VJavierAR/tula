from odoo import models, fields, api,_
import datetime, time
from odoo import exceptions
from odoo.exceptions import AccessDenied
import logging, ast
_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
	_inherit='product.product'

	x_preciominimo = fields.Float(
		string='Precio mínimo',
		compute='_compute_x_preciominimo'
	)

	@api.depends('standard_price', 'x_studio_utilidad_')
	def _compute_x_preciominimo(self):
		for r in self:
			r.x_preciominimo = (r.standard_price * r.x_studio_utilidad_ / 100) + r.standard_price

class ProductTemplate(models.Model):
	_inherit='product.template'

	x_studio_precio_mnimo = fields.Float(
		string='Precio mínimo',
		related='product_variant_id.x_preciominimo'
	)

	x_studio_utilidad_ = fields.Float(
		string='Utilidad (%)',
		store=True
	)



class StockMove(models.Model):
	_inherit='stock.move'

	sale_line_id_new = fields.Many2one(
		comodel_name='sale.order.line',
		#ondelete='restrict',
		string='New many2one',
		store=True,
		#copy=True,
		#required=False,
		#track_visibility='onchange'
	)

class SaleOrderLine(models.Model):
	_inherit='sale.order.line'

	x_studio_field_HNW2r = fields.One2many(
		comodel_name='stock.move',
		inverse_name='sale_line_id_new',
		string='New UnoAMuchos',
		store=True
	)

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
	
	x_studio_field_fAMfd = fields.Many2many(
		comodel_name='stock.warehouse',
		relation ='x_sale_order_line_stock_warehouse_rel',
		column1='sale_order_line_id',
		column2='stock_warehouse_id',
		string='Almacén',
		store=True
	)

	x_studio_field_hBl4n = fields.Many2many(
		comodel_name='res.company',
		relation ='x_res_company_sale_order_line_rel',
		column1='sale_order_line_id',
		column2='res_company_id',
		string='Compañías',
		store=True
	)

	x_studio_field_iF4QS  = fields.Many2many(
		comodel_name='stock.warehouse',
		relation ='x_sale_order_line_stock_warehouse_rel_1',
		column1='sale_order_line_id',
		column2='stock_warehouse_id',
		string='Almacén',
		store=True
	)

	x_value1_id = fields.Char(
		string='valor1',
		#compute="_compute_x_value1_id"
	)

	@api.onchange('qty_available_today', 'product_uom_qty')
	def _compute_x_value1_id(self):
		for record in self:
			if record.qty_available_today >= 1 and record.product_uom_qty > record.qty_available_today:
				record.x_value1_id = 'No hay suficiente stock'
			elif record.qty_available_today >= 1 and record.product_uom_qty <= record.qty_available_today:
				record.x_value1_id = 'Si hay stock'
			else:
				record.x_value1_id = 'No hay stock'

	x_studio_motivo_de_perdida_de_la_orden = fields.Selection(
		selection=[('1','1')],
		string = 'Motivo de perdida de la orden',
		readonly=True
	)

	x_studio_motivo_de_perdida = fields.Selection(
		selection=[('No hay stock', 'No hay stock'),('Tiempo de espera', 'Tiempo de espera'),('Costo elevado', 'Costo elevado')],
		string='Motivo de perdida'
	)

	x_value7_id = fields.Integer(string='Cantidad disponible por sucursal')

	x_value2_id = fields.Integer(string='cantidad perdida')

	@api.onchange('product_uom_qty', 'qty_delivered')
	def resta(self):
		self.x_value2_id = self.product_uom_qty - self.qty_delivered

	x_tiempo_total = fields.Integer(string='Tiempo de entrega')

	@api.onchange('x_studio_tiempo_de_entrega_del_proveedor', 'qty_available_today', 'customer_lead')
	def minimos(self):
		if self.qty_available_today == 0:
			self.x_tiempo_total = self.customer_lead + self.x_studio_tiempo_de_entrega_del_proveedor
		elif self.qty_available_today >= self.product_uom_qty:
			self.x_tiempo_total = self.customer_lead
		else:
			self.x_tiempo_total = self.customer_lead + self.x_studio_tiempo_de_entrega_del_proveedor


	x_studio_tiempo_de_entrega_del_proveedor = fields.Integer(
		string='Tiempo de entrega del proveedor',
		related='product_id.seller_ids.delay'
	)

	x_studio_field_qSqYi = fields.Boolean(
		string='New Campo relacionado',
		related='x_studio_field_U1p5V.lot_stock_id.quant_ids.on_hand'
	)

	x_studio_field_qSqYi = fields.Boolean(
		string='New Campo relacionado',
		related='x_studio_field_U1p5V.lot_stock_id.quant_ids.on_hand'
	)

	x_studio_field_gj0dW = fields.Boolean(
		string='New Campo relacionado',
		#related='warehouse_id.lot_stock_id.quant_ids.on_hand'
	)

	x_studio_field_c1fDg = fields.Boolean(
		string='New Campo relacionado',
		#related='warehouse_id.view_location_id.quant_ids.on_hand'
	)

	x_studio_field_TiwJ0 = fields.Boolean(
		string='New Campo relacionado',
		#related='warehouse_id.lot_stock_id.child_ids.quant_ids.on_hand'
	)

	x_studio_field_JtVY2 = fields.Boolean(
		string='New Campo relacionado',
		#related='warehouse_id.lot_stock_id.quant_ids.on_hand'
	)

	x_studio_precio_mnimo = fields.Float(
		string='Precio mínimo',
		related='product_id.x_studio_precio_mnimo'
	)

	x_precio_con_descuento = fields.Float(
		string='Precio con descuento',
		readonly=True,
		store=True,
		compute="_compute_x_precio_con_descuento"
	)

	@api.depends("price_subtotal", "product_uom_qty")
	def _compute_x_precio_con_descuento(self):
		for record in self:
			record.x_precio_con_descuento = record.price_subtotal / record.product_uom_qty

	x_value3_id = fields.Float(
		string="Monto perdido",
		readonly=True,
		store=True,
		compute="_compute_x_value3_id"
	)

	@api.depends("x_value2_id", "price_unit")
	def _compute_x_value3_id(self):
		for record in self:
			record.x_value3_id = record.x_value2_id * record.price_unit


	x_value4_id = fields.Float(
		string="Venta total",
		readonly=True,
		store=True,
		compute="_compute_x_value4_id"
	)


	@api.depends("qty_delivered", "price_unit")
	def _compute_x_value4_id(self):
		for record in self:
			record.x_value4_id = record.qty_delivered * record.price_unit


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

	x_studio_motivo_de_perdida_de_la_orden = fields.Selection(
		selection=[('Falta de seguimiento', 'Falta de seguimiento'), ('Productos incompletos', 'Productos incompletos'),('Orden perdida', 'Orden perdida')],
		string = 'Motivo de perdida de la orden',
		readonly=True
	)
	"""
	x_studio_field_QXqCU = fields.Float(
		string='New Campo relacionado',
		readonly=True,
		related='product_id.quantity_svl'
	)
	"""
class PurachaseOrderLine(models.Model):
	_inherit = 'purachase.order.line'

	x_studio_field_2ZpSa = fields.Float(
		string='Precio de compra antes de costes de envío',
		readonly=True,
		related='product_id.standard_price'
	)
