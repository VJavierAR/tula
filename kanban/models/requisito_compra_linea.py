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


class RequisitoCompraLinea(models.Model):
    _name = 'requisito.compra.linea'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Requisito de compra línea'

    # Campos en tree
    requisito_compra_rel = fields.Many2one(
        comodel_name="requisito.compra",
        string="Pedido abierto rel",
        required=False,
        store=True,
        index=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        change_default=True,
        ondelete='restrict',
        check_company=True,
        store=True,
        copy=True,
        required=True
    )
    numero_de_parte = fields.Char(
        string="Número de parte",
        store=True,
        copy=True,
        help="Código del cliente"
    )
    cantidad_inventario = fields.Integer(
        string="Cantidad inventario",
        default=0,
        store=True,
        copy=True,
        help="Cantidad de inventario del cliente"
    )
    a_facturar = fields.Integer(
        string="A facturar",
        default=0,
        store=True,
        copy=True,
        readonly=True,
        help="Cantidad requerida"
    )
    cantidad_a_restar_o_sumar = fields.Integer(
        string="Cantidad a restar o sumar",
        default=0,
        store=True,
        copy=True,
    )
    punto_reorden = fields.Integer(
        string="Punto reorden",
        default=0,
        store=True,
        copy=True,
    )
    precio_usd = fields.Float(
        string="Precio USD",
        default=0,
        store=True,
        copy=True,
        related="p_a_linea_programado.price_unit"
    )
    realizado = fields.Boolean(
        string="Realizado",
        default=False,
        store=True,
        copy=False
    )
    revisado = fields.Boolean(
        string="Revisado",
        default=False,
        store=True,
        copy=False
    )
    saldo_pedido_abierto = fields.Integer(
        string="Saldo PO",
        default=0,
        store=True,
        copy=True,
    )
    fecha_de_solicitud = fields.Date(
        string="Fecha de solicitud",
        store=True,
        copy=True,
    )
    saldo_actual_pedido_abierto = fields.Integer(
        string="Saldo actual PO",
        default=0,
        store=True,
        copy=True,
    )

    # Campos en form
    order_partner_id = fields.Many2one(
        related='requisito_compra_rel.partner_id',
        store=True,
        string='Cliente',
        readonly=False
    )
    name = fields.Char(
        string='Descripción',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _('New')
    )
    unidad_de_medidad = fields.Char(
        string="Unidad de medida",
        copy=True,
        readonly=True,
        store=True
    )
    comentarios = fields.Text(
        string="Comentarios",
        store=True,
    )
    p_a_linea_programado = fields.Many2one(
        comodel_name="pedido.abierto.linea",
        string="1. Línea de Pedido Programado",
        store=True,
        copy=True,
        domain="[('order_partner_id', '=', order_partner_id), ('product_id', '=', product_id)]"
    )
    p_c_linea_programado = fields.Text(
        string="1. Pedido Cliente",
        related="p_a_linea_programado.pedido_cliente",
        store=True,
        copy=True,
    )
    r_linea_programado = fields.Integer(
        string="1. Cantidad restante de PO",
        related="p_a_linea_programado.cantidad_restante",
        store=True,
        copy=True,
    )
    saldo_actual_pedido_l_p = fields.Integer(
        string="Saldo actual pedido",
        related="p_a_linea_programado.cantidad_restante",
        store=True,
        copy=True,
    )
    cantidad_facturada_l_p = fields.Integer(
        string="A facturar",
        related="p_a_linea_programado.cantidad_facturada",
        store=True,
        copy=True,
    )
    cancelado = fields.Boolean(
        string="Cancelado",
        store=True,
        default=False
    )
    p_a_linea_programado_dos = fields.Many2one(
        comodel_name="pedido.abierto.linea",
        string="2. Línea de Pedido Programado",
        store=True,
        copy=True,
        domain="[('order_partner_id', '=', order_partner_id), ('product_id', '=', product_id)]"
    )
    p_c_linea_programado_dos = fields.Text(
        string="2. Pedido Cliente",
        related="p_a_linea_programado.pedido_cliente",
        store=True,
        copy=True,
    )
    r_linea_programado_dos = fields.Integer(
        string="2. Cantidad restante de PO",
        related="p_a_linea_programado.cantidad_restante",
        store=True,
        copy=True,
    )
    p_a_linea_programado_tres = fields.Many2one(
        comodel_name="pedido.abierto.linea",
        string="3. Línea de Pedido Programado",
        store=True,
        copy=True,
        domain="[('order_partner_id', '=', order_partner_id), ('product_id', '=', product_id)]"
    )
    p_c_linea_programado_tres = fields.Text(
        string="3. Pedido Cliente",
        related="p_a_linea_programado.pedido_cliente",
        store=True,
        copy=True,
    )
    r_linea_programado_tres = fields.Integer(
        string="3. Cantidad restante de PO",
        related="p_a_linea_programado.cantidad_restante",
        store=True,
        copy=True,
    )
    cantidad_pendiente_de_recibir = fields.Integer(
        string="Cantidad pendiente de recibir",
        store=True
    )
    cantidad_realizada = fields.Integer(
        string="Cantidad realizada",
        store=True
    )
    cantidad_cancelada = fields.Integer(
        string="Cantidad cancelada",
        store=True
    )
    state_requisito_compra = fields.Selection(
        selection=[
            ('borrador', 'borrador'),
            ('por_ser_aprobado', 'por ser aprobado'),
            ('aprobado', 'aprobado'),
            ('rechazado', 'rechazado'),
            ('realizado', 'realizado')
        ],
        string="Estado",
        readonly=True,
        store=True,
        copy=False,
        related="requisito_compra_rel.state",
    )

    @api.model
    def create(self, vals):
        if 'product_id' in vals:
            producto = self.env['product.product'].search([
                ('id', '=', vals.get('product_id'))
            ])
            vals['name'] = str(producto.display_name)
            
        result = super(RequisitoCompraLinea, self).create(vals)
        return result

    @api.onchange('product_id')
    def cambia_producto(self):
        if self.product_id.id:

            # Obtiene código de cliente
            numeros_de_parte = []
            for codigo in self.product_id.codigos_de_producto:
                if self.order_partner_id.id == codigo.cliente.id:
                    numeros_de_parte.append(codigo.codigo_producto)
            self.numero_de_parte = str(numeros_de_parte)

            # Obtiene unidad de medida
            if self.product_id.uom_po_id.id:
                self.unidad_de_medidad = self.product_id.uom_po_id.name

            # Obtiene la cantidad en ordenes

    @api.onchange('cantidad_a_restar_o_sumar', 'cantidad_inventario')
    def actualiza_cantidad_a_facturar(self):
        cantidad_solicitada = self.punto_reorden - self.cantidad_inventario
        cantidad_solicitada += self.cantidad_a_restar_o_sumar
        self.a_facturar = cantidad_solicitada

    @api.onchange('product_id', 'cantidad_inventario')
    def cambia_a_realizado(self):
        if self.product_id.id and self.cantidad_inventario != 0:
            self.realizado = True
        else:
            self.realizado = False
