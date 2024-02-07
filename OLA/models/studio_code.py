from odoo import models, fields, api,_
import datetime, time
from odoo import exceptions
from odoo.exceptions import AccessDenied
from odoo.tools import float_is_zero, float_repr
import logging, ast
_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
	_inherit = 'product.product'
	nuevo_costo_facturacion=fields.Float(default=0,string='Precio Compra',company_dependent=True,check_company=True)
	nuevo_costo_facturacion_impuesto=fields.Float(default=0,string='Precio Venta+impuesto',company_dependent=True,check_company=True)
	check=fields.Boolean(default=False)
	x_preciominimo = fields.Float(
		string='Precio mínimo',
		store=True,
		company_dependent=True,
		check_company=True,
		#compute='_compute_x_preciominimo'
	)
	"""
	x_studio_precio_mnimo = fields.Float(
		string='Precio mínimo',
		# related='product_variant_id.x_preciominimo',
		store=True,
		company_dependent=True,
		#check_company=True,
		#compute='_compute_x_preciominimo'
	)
	x_studio_utilidad_ = fields.Float(
		string='Utilidad precio mínimo (%)',
		store=True,
		company_dependent=True,
		check_company=True
	)

	list_price = fields.Float(
		string="Precio de venta",
		store=True,
		copy=True,
		company_dependent=True,
		#check_company=True,
	)
	"""
	x_studio_utilidad_precio_de_venta = fields.Float(
		string='Utilidad precio de venta (%)',
		store=True,
		company_dependent=True,
		check_company=True
	)
	

	"""
	@api.depends('standard_price', 'x_studio_utilidad_')
	def _compute_x_preciominimo(self):
		for rec in self:
			if rec.standard_price and rec.x_studio_utilidad_:
				caulculo = (rec.standard_price * rec.x_studio_utilidad_ / 100) + rec.standard_price
				rec['x_preciominimo'] = caulculo
				rec['x_studio_precio_mnimo'] = caulculo

	@api.onchange('standard_price', 'x_studio_utilidad_precio_de_venta')
	def cambio_precio_de_venta(self):
		self.list_price = (self.standard_price * self.x_studio_utilidad_precio_de_venta / 100) + self.standard_price
	"""
	def write(self, vals):
		if('x_studio_utilidad_precio_de_venta' in vals):
			if(vals['x_studio_utilidad_precio_de_venta']==0):
				del vals['x_studio_utilidad_precio_de_venta']
		if('list_price' in vals):
			if(vals['list_price']==0):
				del vals['list_price']
		check=vals['check'] if('check' in vals) else False
		if('nuevo_costo_facturacion_impuesto' in vals):
			if(vals['nuevo_costo_facturacion_impuesto']==0 and check!=True):
				del vals['nuevo_costo_facturacion_impuesto']
		precio=vals['nuevo_costo_facturacion_impuesto'] if('nuevo_costo_facturacion_impuesto' in vals) else self.nuevo_costo_facturacion_impuesto
		if 'standard_price' in vals and precio==0:
			#_logger.info("self.id: " + str(self.id))
			producto = self.env['product.template'].search([('id', '=', self.product_tmpl_id.id)])
			#_logger.info("producto: " + str(producto))
			# actualiza precio de venta
			coste = vals['standard_price']
			vals['list_price'] = (coste * producto.x_studio_utilidad_precio_de_venta / 100) + coste
			producto.list_price = (coste * producto.x_studio_utilidad_precio_de_venta / 100) + coste
			# actualiza precio minimo
			vals['x_studio_precio_mnimo'] = (coste * producto.x_studio_utilidad_ / 100) + coste
			producto.x_studio_precio_mnimo = (coste * producto.x_studio_utilidad_ / 100) + coste

			vals['x_studio_utilidad_precio_de_venta'] = producto.x_studio_utilidad_precio_de_venta
			vals['x_studio_utilidad_'] = producto.x_studio_utilidad_
			#_logger.info(
			#	"standard_price: " + str(coste) +
			#	" self.x_studio_utilidad_precio_de_venta: " + str(producto.x_studio_utilidad_precio_de_venta) +
			#	" self.x_studio_utilidad_: " + str(producto.x_studio_utilidad_) +
			#	" vals: " + str(vals)
			#)
		res = super(ProductProduct, self).write(vals)
		#_logger.info("res: " + str(res))
		return res




	# def write(self,vals):
	# 	_logger.info(vals)

	# 	res=super(ProductProduct,self).write(vals)
	# 	return res 

	# @api.depends('standard_price', 'x_studio_utilidad_')
	@api.onchange('standard_price', 'x_studio_utilidad_')
	@api.depends_context('force_company')
	def _compute_x_preciominimo(self):
		company = self.env.context.get('force_company', False)
		for rec in self:
			if rec.with_context(force_company=self.env.company.id).standard_price and rec.with_context(
					force_company=self.env.company.id).x_studio_utilidad_:
				rec.x_studio_precio_mnimo = (rec.with_context(
					force_company=self.env.company.id).standard_price * rec.with_context(
					force_company=self.env.company.id).x_studio_utilidad_ / 100) + rec.with_context(
					force_company=self.env.company.id).standard_price

	@api.onchange('standard_price', 'x_studio_utilidad_precio_de_venta')
	@api.depends_context('force_company')
	def cambio_precio_de_venta(self):
		company = self.env.context.get('force_company', False)
		for rec in self:
			if rec.with_context(force_company=self.env.company.id).standard_price and rec.with_context(
					force_company=self.env.company.id).x_studio_utilidad_precio_de_venta:
				rec.list_price = (rec.with_context(
					force_company=self.env.company.id).standard_price * rec.with_context(
					force_company=self.env.company.id).x_studio_utilidad_precio_de_venta / 100) + rec.with_context(
					force_company=self.env.company.id).standard_price
		# self.list_price = (self.standard_price * self.x_studio_utilidad_precio_de_venta / 100) + self.standard_price

	def actualiza_precio_de_venta_y_precio_minimo(self):
		self._compute_x_preciominimo()
		self.cambio_precio_de_venta()


class ProductTemplate(models.Model):
	_inherit = 'product.template'
	nuevo_costo_facturacion=fields.Float(default=0,string='Precio Compra',company_dependent=True,check_company=True)
	nuevo_costo_facturacion_impuesto=fields.Float(default=0,string='Precio Venta+impuesto',company_dependent=True,check_company=True)
	check=fields.Boolean(default=False)
	x_studio_precio_mnimo = fields.Float(
		string='Precio mínimo',
		store=True,
		company_dependent=True,
		#check_company=True,
		#compute='_compute_x_preciominimo'
	)

	x_studio_utilidad_ = fields.Float(
		string='Utilidad precio mínimo (%)',
		store=True,
		company_dependent=True,
		check_company=True
	)

	list_price = fields.Float(
		string="Precio de venta",
		store=True,
		copy=True,
		company_dependent=True,
		#check_company=True,
	)
	x_studio_utilidad_precio_de_venta = fields.Float(
		string='Utilidad precio de venta (%)',
		store=True,
		company_dependent=True,
		check_company=True
	)

	#@api.depends('standard_price', 'x_studio_utilidad_')
	@api.onchange('standard_price', 'x_studio_utilidad_')
	@api.depends_context('force_company')
	def _compute_x_preciominimo(self):
		company = self.env.context.get('force_company', False)
		for rec in self:
			if rec.with_context(force_company=self.env.company.id).standard_price and rec.with_context(force_company=self.env.company.id).x_studio_utilidad_:
				rec.with_context(force_company=self.env.company.id).x_studio_precio_mnimo = (rec.with_context(force_company=self.env.company.id).standard_price * rec.with_context(force_company=self.env.company.id).x_studio_utilidad_ / 100) + rec.with_context(force_company=self.env.company.id).standard_price

	@api.onchange('standard_price', 'x_studio_utilidad_precio_de_venta')
	@api.depends_context('force_company')
	def cambio_precio_de_venta(self):
		company = self.env.context.get('force_company', False)
		for rec in self:
			if rec.with_context(force_company=self.env.company.id).standard_price and rec.with_context(force_company=self.env.company.id).x_studio_utilidad_precio_de_venta:
				rec.with_context(force_company=self.env.company.id).list_price = (rec.with_context(force_company=self.env.company.id).standard_price * rec.with_context(force_company=self.env.company.id).x_studio_utilidad_precio_de_venta / 100) + rec.with_context(force_company=self.env.company.id).standard_price
				# self.list_price = (self.standard_price * self.x_studio_utilidad_precio_de_venta / 100) + self.standard_price

	def actualiza_precio_de_venta_y_precio_minimo(self):
		self._compute_x_preciominimo()
		self.cambio_precio_de_venta()
        
	def write(self, vals):
		if('x_studio_utilidad_precio_de_venta' in vals):
			if(vals['x_studio_utilidad_precio_de_venta']==0):
				del vals['x_studio_utilidad_precio_de_venta']
		if('list_price' in vals):
			if(vals['list_price']==0):
				del vals['list_price']
		if('nuevo_costo_facturacion_impuesto' in vals):
			if(vals['nuevo_costo_facturacion_impuesto']==0):
				del vals['nuevo_costo_facturacion_impuesto']
		#precio=vals['nuevo_costo_facturacion_impuesto'] if('nuevo_costo_facturacion_impuesto' in vals) else self.nuevo_costo_facturacion_impuesto
		# if 'standard_price' in vals and precio==0:
		# 	#_logger.info("self.id: " + str(self.id))
		# 	producto = self.product_variant_id
		# 	#_logger.info("producto: " + str(producto))
		# 	# actualiza precio de venta
		# 	coste = vals['standard_price']
		# 	vals['list_price'] = (coste * producto.x_studio_utilidad_precio_de_venta / 100) + coste
		# 	producto.list_price = (coste * producto.x_studio_utilidad_precio_de_venta / 100) + coste
		# 	# actualiza precio minimo
		# 	vals['x_studio_precio_mnimo'] = (coste * producto.x_studio_utilidad_ / 100) + coste
		# 	producto.x_studio_precio_mnimo = (coste * producto.x_studio_utilidad_ / 100) + coste

		# 	vals['x_studio_utilidad_precio_de_venta'] = producto.x_studio_utilidad_precio_de_venta
		# 	vals['x_studio_utilidad_'] = producto.x_studio_utilidad_
			#_logger.info(
			#	"standard_price: " + str(coste) +
			#	" self.x_studio_utilidad_precio_de_venta: " + str(producto.x_studio_utilidad_precio_de_venta) +
			#	" self.x_studio_utilidad_: " + str(producto.x_studio_utilidad_) +
			#	" vals: " + str(vals)
			#)
		res = super(ProductTemplate, self).write(vals)
		#_logger.info("res: " + str(res))
		return res

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
		store=True
		#compute="_compute_x_value1_id"
	)

	@api.onchange('qty_available_today', 'product_uom_qty', 'product_id')
	def _compute_x_value1_id(self):
		#for record in self:
		if self.product_id.id:
			if self.sudo().qty_available_today >= 1 and self.product_uom_qty > self.sudo().qty_available_today:
				self.x_value1_id = 'No hay suficiente stock'
			elif self.qty_available_today >= 1 and self.product_uom_qty <= self.qty_available_today:
				self.x_value1_id = 'Si hay stock'
			else:
				self.x_value1_id = 'No hay stock'

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

	@api.onchange('product_uom_qty', 'qty_delivered', 'product_id')
	def resta(self):
		if self.product_id.id:
			self.x_value2_id = self.product_uom_qty - self.qty_delivered

	x_tiempo_total = fields.Integer(string='Tiempo de entrega')

	@api.onchange('x_studio_tiempo_de_entrega_del_proveedor', 'qty_available_today', 'customer_lead', 'product_id')
	def minimos(self):
		if self.product_id.id:
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
		#compute="_compute_x_precio_con_descuento"
	)

	@api.onchange("price_subtotal", "product_uom_qty", 'product_id')
	def _compute_x_precio_con_descuento(self):
		#for record in self:
		if self.product_id.id:
			self.x_precio_con_descuento = self.price_subtotal / self.product_uom_qty

	x_value3_id = fields.Float(
		string="Monto perdido",
		readonly=True,
		store=True,
		#compute="_compute_x_value3_id"
	)

	@api.onchange("x_value2_id", "price_unit", 'product_id')
	def _compute_x_value3_id(self):
		#for record in self:
		if self.product_id.id:
			self.x_value3_id = self.x_value2_id * self.price_unit


	x_value4_id = fields.Float(
		string="Venta total",
		readonly=True,
		store=True,
		#compute="_compute_x_value4_id"
	)

	@api.onchange("qty_delivered", "price_unit", 'product_id')
	def _compute_x_value4_id(self):
		#for record in self:
		if self.product_id.id:
			self.x_value4_id = self.qty_delivered * self.price_unit


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
	_inherit = 'purchase.order.line'

	x_studio_field_2ZpSa = fields.Float(
		string='Precio de compra antes de costes de envío',
		readonly=True,
		related='product_id.standard_price'
	)
