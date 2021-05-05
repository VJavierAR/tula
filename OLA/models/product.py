from odoo import models, fields, api,_
import logging, ast
_logger = logging.getLogger(__name__)

codigo_buscado = ""
codigos_buscados_lista = []

class product(models.Model):
	_inherit = 'product.template'
	#_rec_name = "name" #despliega e display_name en las busquedas de campos many2one

	codigo_producto_cliente = fields.Text(
		string = "Código de cliente",
		store = True,
		#track_visibility = 'onchange'
	)

	codigos_de_producto = fields.One2many(
		comodel_name='product.codigos',
		inverse_name='producto_id',
		string='Códigos de producto',
		#context =dict([('default_producto_id', id)])
	)

	@api.model
	def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
		global codigos_buscados_lista
		# codigos_buscados_lista = []
		args = args or []
		recs = self.browse()
		if not recs:
			codigos_producto = self.env['product.codigos'].search([])
			codigos_producto = codigos_producto.filtered(
				lambda codigo: name.lower() == codigo.codigo_producto.lower()).mapped('producto_id.id')
			recs = self.search(['|', '|', '|', '|',
								('name', operator, name),
								('default_code', operator, name),
								('codigo_producto_cliente', operator, name),
								('barcode', operator, name),
								('id', 'in', codigos_producto)
								] + args, limit=limit)
			global codigo_buscado
			codigo_buscado = name.lower()
			for rec in recs:
				if codigo_buscado:
					codigos_buscados_lista.append(
						{
							'id_producto': rec.id,
							'codigo_buscado': codigo_buscado
						}
					)

		return recs.name_get()

	"""
	def name_get(self, codigo_cliente=None):
		productos_lista = []
		for producto in self:
			_logger.info("self: " + str(self) + " producto: " + str(producto))
			codigo = producto.default_code
			nombre = producto.name

			global codigos_buscados_lista
			_logger.info("1: codigo_cliente: " + str(codigo_cliente) + " codigo_buscado global: " + str(codigo_buscado) +
						 " codigos_buscados_lista: " + str(codigos_buscados_lista))
			if not codigo_cliente and codigos_buscados_lista:
				for codigo in codigos_buscados_lista:
					if codigo['id_producto'] == producto.id:
						codigo_cliente = codigo['codigo_buscado']
			elif not codigo_cliente and codigo_buscado:
				codigo_cliente = codigo_buscado
			if codigo_cliente:
				productos_lista.append(
					[
						producto.id,
						'[%s] %s' %
						(
							codigo_cliente,
							nombre
						)
					]
				)
			else:
				productos_lista.append(
					[
						producto.id,
						'[%s] %s' %
						(
							codigo,
							nombre
						)
					]
				)
		return productos_lista
	"""

	"""
	def name_get(self):
		# TDE: this could be cleaned a bit I think

		def _name_get(d):
			name = d.get('name', '')
			code = self._context.get('display_default_code', True) and d.get('default_code', False) or False
			if code:
				name = '[%s] %s' % (code, name)
			return (d['id'], name)

		partner_id = self._context.get('partner_id')
		if partner_id:
			partner_ids = [partner_id, self.env['res.partner'].browse(partner_id).commercial_partner_id.id]
		else:
			partner_ids = []
		company_id = self.env.context.get('company_id')

		# all user don't have access to seller and partner
		# check access and use superuser
		self.check_access_rights("read")
		self.check_access_rule("read")

		result = []

		# Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
		# Use `load=False` to not call `name_get` for the `product_tmpl_id`
		self.sudo().read(['name', 'default_code', 'product_tmpl_id'], load=False)

		product_template_ids = self.sudo().mapped('product_tmpl_id').ids

		if partner_ids:
			supplier_info = self.env['product.supplierinfo'].sudo().search([
				('product_tmpl_id', 'in', product_template_ids),
				('name', 'in', partner_ids),
			])
			# Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
			# Use `load=False` to not call `name_get` for the `product_tmpl_id` and `product_id`
			supplier_info.sudo().read(['product_tmpl_id', 'product_id', 'product_name', 'product_code'], load=False)
			supplier_info_by_template = {}
			for r in supplier_info:
				supplier_info_by_template.setdefault(r.product_tmpl_id, []).append(r)
		for product in self.sudo():
			variant = product.product_template_attribute_value_ids._get_combination_name()

			name = variant and "%s (%s)" % (product.name, variant) or product.name
			sellers = []
			if partner_ids:
				product_supplier_info = supplier_info_by_template.get(product.product_tmpl_id, [])
				sellers = [x for x in product_supplier_info if x.product_id and x.product_id == product]
				if not sellers:
					sellers = [x for x in product_supplier_info if not x.product_id]
				# Filter out sellers based on the company. This is done afterwards for a better
				# code readability. At this point, only a few sellers should remain, so it should
				# not be a performance issue.
				if company_id:
					sellers = [x for x in sellers if x.company_id.id in [company_id, False]]
			if sellers:
				for s in sellers:
					seller_variant = s.product_name and (
							variant and "%s (%s)" % (s.product_name, variant) or s.product_name
					) or False
					mydict = {
						'id': product.id,
						'name': seller_variant or name,
						'default_code': s.product_code or product.default_code,
					}
					temp = _name_get(mydict)
					if temp not in result:
						result.append(temp)
			else:
				mydict = {
					'id': product.id,
					'name': name,
					'default_code': product.default_code,
				}
				result.append(_name_get(mydict))
		return result
	"""


class productPr(models.Model):
	_inherit = 'product.product'
	sug_rel=fields.Many2many('product.product',relation='product_may_sug',column1='id', column2='id2')
	alt_rel=fields.Many2many('product.product',relation='product_alte_rel',column1='id', column2='id2')

	@api.model
	def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
		global codigos_buscados_lista
		#codigos_buscados_lista = []
		args = args or []
		recs = self.browse()
		if not recs:
			codigos_producto = self.env['product.codigos'].search([])
			codigos_producto = codigos_producto.filtered(
				lambda codigo: name.lower() == codigo.codigo_producto.lower()).mapped('producto_id.id')
			recs = self.search(['|', '|', '|', '|',
								('name', operator, name),
								('default_code', operator, name),
								('codigo_producto_cliente', operator, name),
								('barcode', operator, name),
								('id', 'in', codigos_producto)
								] + args, limit=limit)
			global codigo_buscado
			codigo_buscado = name.lower()
			for rec in recs:
				if codigo_buscado:
					codigos_buscados_lista.append(
						{
							'id_producto': rec.id,
							'codigo_buscado': codigo_buscado
						}
					)

		return recs.name_get()

	"""
	def name_get(self, codigo_cliente=None):
		productos_lista = []
		for producto in self:
			_logger.info("self: " + str(self) + " producto: " + str(producto))
			codigo = producto.default_code
			nombre = producto.name
			global codigo_buscado
			global codigos_buscados_lista
			_logger.info("2: codigo_cliente: " + str(codigo_cliente) + " codigo_buscado global: " + str(codigo_buscado) +
						 " codigos_buscados_lista: " + str(codigos_buscados_lista))
			if not codigo_cliente and codigo_buscado:
				codigo_cliente = codigo_buscado
			if codigo_cliente:
				productos_lista.append(
					[
						producto.id,
						'[%s] %s' %
						(
							codigo_cliente,
							nombre
						)
					]
				)
			else:
				productos_lista.append(
					[
						producto.id,
						'[%s] %s' %
						(
							codigo,
							nombre
						)
					]
				)
		return productos_lista
	"""
class codigos(models.Model):
	_name='product.codigos'
	_description='Lista de codigos para los clientes'

	producto_id = fields.Many2one(
		comodel_name = 'product.template',
		string = 'Producto relacionado'
	)
	cliente = fields.Many2one(
		comodel_name = 'res.partner',
		string = 'Cliente',
		track_visibility = 'onchange'
	)

	codigo_producto = fields.Text(
		string = "Código de producto",
		store = True,
		track_visibility = 'onchange'
	)
