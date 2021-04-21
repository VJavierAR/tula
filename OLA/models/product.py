from odoo import models, fields, api,_
import logging, ast
_logger = logging.getLogger(__name__)


class product(models.Model):
	_inherit = 'product.template'

	codigo_producto_cliente = fields.Text(
		string = "Código de cliente",
		store = True,
		#track_visibility = 'onchange'
	)

	@api.model
	def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
		args = args or []
		domain = []
		_logger.info("args: " + str(args))
		if name:
			domain['|', '|', '|',
				   ('name', operator, name),
				   ('default_code', operator, name),
				   ('codigo_producto_cliente', operator, name),
				   ('barcode', operator, name)
			]
			_logger.info("domain: " + str(domain))
		return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)
		"""
		# Only use the product.product heuristics if there is a search term and the domain
		# does not specify a match on `product.template` IDs.
		if not name or any(term[0] == 'id' for term in (args or [])):
			return super(ProductTemplate, self)._name_search(name=name, args=args, operator=operator, limit=limit,
															 name_get_uid=name_get_uid)

		Product = self.env['product.product']
		templates = self.browse([])
		domain_no_variant = [('product_variant_ids', '=', False)]
		while True:
			domain = templates and [('product_tmpl_id', 'not in', templates.ids)] or []
			args = args if args is not None else []
			products_ns = Product._name_search(name, args + domain, operator=operator, name_get_uid=name_get_uid)
			products = Product.browse([x[0] for x in products_ns])
			new_templates = products.mapped('product_tmpl_id')
			if new_templates & templates:
				#Product._name_search can bypass the domain we passed (search on supplier info).
                #   If this happens, an infinite loop will occur.
				break
			templates |= new_templates
			current_round_templates = self.browse([])
			if not products:
				domain_template = args + domain_no_variant + (templates and [('id', 'not in', templates.ids)] or [])
				template_ns = super(ProductTemplate, self)._name_search(name=name, args=domain_template,
																		operator=operator, limit=limit,
																		name_get_uid=name_get_uid)
				current_round_templates |= self.browse([ns[0] for ns in template_ns])
				templates |= current_round_templates
			if (not products and not current_round_templates) or (limit and (len(templates) > limit)):
				break

		searched_ids = set(templates.ids)
		# some product.templates do not have product.products yet (dynamic variants configuration),
		# we need to add the base _name_search to the results
		# FIXME awa: this is really not performant at all but after discussing with the team
		# we don't see another way to do it
		if not limit or len(searched_ids) < limit:
			searched_ids |= set([template_id[0] for template_id in
								 super(ProductTemplate, self)._name_search(
									 name,
									 args=args,
									 operator=operator,
									 limit=limit,
									 name_get_uid=name_get_uid)])

		# re-apply product.template order + name_get
		return super(ProductTemplate, self)._name_search(
			'', args=[('id', 'in', list(searched_ids))],
			operator='ilike', limit=limit, name_get_uid=name_get_uid)
		"""

class productPr(models.Model):
	_inherit = 'product.product'
	sug_rel=fields.Many2many('product.product',relation='product_may_sug',column1='id', column2='id2')

	@api.model
	def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
		args = args or []
		domain = []
		_logger.info("args: " + str(args))
		if name:
			domain['|', '|', '|',
				   ('name', operator, name),
				   ('default_code', operator, name),
				   ('codigo_producto_cliente', operator, name),
				   ('barcode', operator, name)
			]
			_logger.info("domain: " + str(domain))
		return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)