# -*- coding: utf-8 -*-

from odoo import models, fields, api
from email.utils import formataddr
from odoo.exceptions import UserError, RedirectWarning
from odoo import exceptions, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging, ast
import pytz
import base64
import requests
import json

_logger = logging.getLogger(__name__)


class PedidoAbiertoLinea(models.Model):
    _name = 'pedido.abierto.linea'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'lineas de pedido abierto'

    @api.onchange('product_id')
    def _get_name(self):
        if self.product_id.id:
            self.name = self.product_id.name
        else:
            self.name = "No disponible"

    name = fields.Text(
        string='Descripción',
        required=True,
    )
    company_id = fields.Many2one(
        related='pedido_abierto_rel.company_id',
        string='Compañia',
        store=True,
        readonly=True,
        index=True
    )
    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        # domain="[('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        change_default=True,
        ondelete='restrict',
        check_company=True
    )
    product_uom_qty = fields.Float(
        string='Cantidad original',
        digits='Product Unit of Measure',
        required=True,
        default=1.0
    )
    product_uom = fields.Many2one(
        'uom.uom',
        string='Unidad de medida',
        # domain="[('category_id', '=', product_uom_category_id)]"
    )
    """
    product_uom_category_id = fields.Many2one(
        related='product_id.uom_id.category_id',
        readonly=True
    )
    """
    price_unit = fields.Float(
        'Precio',
        required=True,
        digits='Precio producto',
        default=0.0
    )
    """
    price_total = fields.Monetary(
        # compute='_compute_amount',
        string='Total',
        readonly=True,
        store=True
    )
    """

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=None)
            line.update({
                # 'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                # 'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
                    'account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

    tax_id = fields.Many2many(
        'account.tax',
        string='Impuesto',
        domain=['|', ('active', '=', False), ('active', '=', True)]
    )

    order_partner_id = fields.Many2one(
        related='pedido_abierto_rel.partner_id',
        store=True,
        string='Cliente',
        readonly=False
    )
    salesman_id = fields.Many2one(
        related='pedido_abierto_rel.user_id',
        store=True,
        string='Comercial',
        readonly=True
    )
    discount = fields.Float(
        string='Descuento (%)',
        digits='Discount',
        default=0.0
    )
    """
    currency_id = fields.Many2one(
        related='pedido_abierto_rel.currency_id', 
        depends=['order_id.currency_id'], 
        store=True,
        string='Currency', 
        readonly=True
    )
    """




    codigo_cliente = fields.Text(
        string="Código cliente",
        copy=True,
        store=True
    )
    pedido_cliente = fields.Text(
        string="Pedido cliente",
        copy=True,
        store=True
    )
    fecha_programada = fields.Date(
        string="Programación",
        store=True
    )
    codigo_alterno = fields.Text(
        string="Código alterno",
        copy=True,
        store=True
    )
    cantidad_reservada = fields.Integer(
        string="Cantidad reservada",
        copy=True,
        store=True
    )
    default_code_product = fields.Char(
        string="Referencia interna",
        related="product_id.default_code",
        store=True
    )
    confirma_venta_directa = fields.Boolean(
        string="Confirma venta directa",
        default=False,
        store=True
    )
    linea_confirmada = fields.Boolean(
        string="Línea confirmada",
        default=False,
        store=True
    )
    pedido_abierto_rel = fields.Many2one(
        comodel_name="pedido.abierto",
        string="Pedido abierto rel",
        required=False,
        store=True,
        index=True,
    )
    creado_desde_pedido_abierto = fields.Boolean(
        string="Creado desde pedido abierto",
        default=False,
        copy=True,
        store=True
    )
    cantidad_pedida = fields.Integer(
        string="Cantidad pedida",
        default=0,
        copy=True,
        store=True
    )
    cantidad_facturada = fields.Integer(
        string="Cantidad facturada",
        default=0,
        copy=True,
        store=True
    )
    cantidad_entregada = fields.Integer(
        string="Cantidad entregada",
        default=0,
        copy=True,
        store=True
    )
    cantidad_restante = fields.Integer(
        string="Cantidad restante",
        default=0,
        copy=True,
        store=True
    )
    es_de_sale_order = fields.Boolean(
        string="Es de sale order",
        default=False,
        store=True
    )
    linea_relacionada = fields.One2many(
        comodel_name="sale.order.line",
        inverse_name="linea_abierta_rel",
        string="Lineas de pedido abierto",
        store=True

    )

    def create(self, vals):
        _logger.info("vals de pedidod abietto_loina:   \n\n " + str(vals))
        for linea in vals:
            if 'product_uom_qty' in linea:
                linea['cantidad_restante'] = linea['product_uom_qty']
                linea['cantidad_pedida'] = linea['product_uom_qty']

        result = super(PedidoAbiertoLinea, self).create(vals)
        return result

    def crear_pedido_desde_lineas_wizard(self):
        wiz = self.env['orden.abierta.to.directa'].create({})

        view = self.env.ref('orden_abierta.view_orden_abierta_lineas_to_orden_directa_wizard')
        return {
            'name': _('Crear pedido '),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'orden.abierta.to.directa',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
            # 'context': {'default_lineas_pedidos': [(6, 0, self.lineas_pedido.ids)]},
        }

    @api.onchange('product_uom_qty')
    def cambia_cantidad_original(self):
        if len(self.linea_relacionada.ids) == 0:
            self.cantidad_pedida = self.product_uom_qty
            self.cantidad_restante = self.product_uom_qty

    @api.onchange('product_id', 'product_uom_qty')
    def cambia_producto(self):
        if self.product_id.id:
            # self.product_uom
            self.price_unit = self.product_id.lst_price
            if len(self.product_id.taxes_id.ids) > 0:
                self.tax_id = [(6, 0, self.product_id.taxes_id.ids)]

            # Obtiene código de cliente
            for codigo in self.product_id.codigos_de_producto:
                if self.order_partner_id.id == codigo.cliente.id:
                    self.codigo_cliente = codigo.codigo_producto

            # Cantidad reservada
            estados_no_aprobados = ['draft', 'sent']
            ordenes = self.env['sale.order'].search(
                [
                    ('state', 'in', estados_no_aprobados),
                    ('es_orden_abierta', '=', True)
                ])
            cantidad_dispobible = self.product_id.qty_available
            cantidad_reservada_suma = 0
            for orden in ordenes:
                for linea in orden.order_line:
                    if linea.product_id.id == self.product_id.id:
                        cantidad_reservada_suma += linea.product_uom_qty

            if cantidad_reservada_suma > 0:
                self.cantidad_reservada = cantidad_dispobible - cantidad_reservada_suma
            else:
                self.cantidad_reservada = 0

            # Mensaje inventario actual
            cantidad_a_vender = self.product_uom_qty
            cantidad_prevista = self.product_id.virtual_available
            cantidad_entrada = self.product_id.incoming_qty
            cantidad_pedidos_abiertos = cantidad_reservada_suma
            cantidad_disponible_menos_cantidad_pa = cantidad_dispobible - cantidad_pedidos_abiertos
            _logger.info(
                "cantidad_a_vender: " + str(cantidad_a_vender) + " > cantidad_disponible_menos_cantidad_pa:" + str(
                    cantidad_disponible_menos_cantidad_pa))
            if cantidad_a_vender > cantidad_disponible_menos_cantidad_pa:

                nombre_producto = self.product_id.name
                almacenes_stock = self.product_id.stock_quant_ids.filtered(
                    lambda x:
                    x.company_id.id is not False and
                    x.quantity >= 0 and
                    x.location_id.usage == 'internal'
                )
                nombre_almacen = ""
                for data in almacenes_stock:
                    nombre_almacen += str(data.location_id.display_name) + ": " + str(data.quantity) + "\n"
                mensaje = "Planea vender " + str(
                    cantidad_a_vender) + " de " + nombre_producto + " pero solo tiene " + str(cantidad_dispobible)
                mensaje += " en los siguientes almacenes:\nAlmacén: cantidad\n" + nombre_almacen + "\n"
                mensaje += "Existen " + str(cantidad_disponible_menos_cantidad_pa)
                mensaje += " disponibles (Cantidad a mano, menos la cantidad de pedidos abiertos).\n\n"
                mensaje += "Cantidad requerida: " + str(cantidad_a_vender) + "\n"
                mensaje += "Cantidad a mano: " + str(cantidad_dispobible) + "\n"
                mensaje += "Cantidad a prevista: " + str(cantidad_prevista) + "\n"
                mensaje += "Total cantidad en tránsito: " + str(cantidad_entrada) + "\n"
                return {
                    'warning': {
                        'title': _('Inventario actual!'),
                        'message': _(mensaje),
                    },
                }
