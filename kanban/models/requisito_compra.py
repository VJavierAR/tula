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


class RequisitoCompra(models.Model):
    _name = 'requisito.compra'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Requisito de compra'

    name = fields.Char(
        string='Referencia de requerimiento',
        required=True,
        copy=False,
        readonly=True,
        states={'borrador': [('readonly', False)]},
        index=True,
        default=lambda self: _('New')
    )
    state = fields.Selection(
        selection=[
            ('borrador', 'borrador'),
            ('por_ser_aprobado', 'por ser aprobado'),
            ('aprobado', 'aprobado'),
            ('rechazado', 'rechazado'),
            ('realizado', 'realizado')
        ],
        string="Estado",
        readonly=True,
        default="borrador",
        store=True,
        copy=False
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Cliente",
        copy=True,
        store=True,
        required=True
    )
    solicitado_por = fields.Many2one(
        comodel_name="res.users",
        string="Solicitado por",
        copy=True,
        store=True
    )
    aprobado_por = fields.Many2one(
        comodel_name="res.users",
        string="Aprobado por",
        store=True,
        copy=True,
    )
    realizado_por = fields.Many2one(
        comodel_name="res.users",
        string="Realizado por",
        store=True
    )
    tipo_de_albaran = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Tipo de albarán",
        copy=True,
        store=True
    )
    origin = fields.Char(
        string="Documento de origen",
        store=True
    )
    descripcion = fields.Text(
        string="Descripción",
        store=True,
        copy=True
    )
    grupo_de_adquisiciones = fields.Many2one(
        comodel_name="procurement.group",
        string="Grupo de adquisiciones",
        copy=True,
        store=True
    )
    lineas_pedido = fields.One2many(
        comodel_name="requisito.compra.linea",
        inverse_name="requisito_compra_rel",
        string="Lineas de requisito de compra",
        store=True,
        copy=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañia',
        required=True,
        index=True,
        default=lambda self: self.env.company
    )
    fecha_de_solicitud = fields.Date(
        string="Fecha de solicitud",
        store=True,
        copy=True,
    )
    num_lineas = fields.Integer(
        string="Número de líneas",
        # default=lambda self: self.get_num_lineas(),
        compute="_compute_get_num_lineas"
    )
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('requisito.compra.seq') or 'New'

        result = super(RequisitoCompra, self).create(vals)
        return result

    def cambia_a_por_aprobar(self):
        self.state = 'por_ser_aprobado'
        
    def cambia_a_aprobado(self):
        self.state = 'aprobado'
        for line in self.lineas_pedido:
            linea.a_facturar += line.cantidad_a_restar_o_sumar

    def cambia_a_rechazado(self):
        self.state = 'rechazado'
    
    def cambia_a_realizado(self):
        self.state = 'realizado'
    
    def cambia_a_reiniciar(self):
        _logger.info('cambia_a_reiniciar')

    def _compute_get_num_lineas(self):
        for rec in self:
            rec.num_lineas = self.env['requisito.compra.linea'].search_count([
                ('requisito_compra_rel', '=', rec.id)
            ])

    def actualiza_saldo_actual_po(self):
        for rec in self.lineas_pedido:
            qty_restante = self.env['pedido.abierto.linea'].search([
                ('product_id', '=', rec.product_id.id),
                ('order_partner_id', '=', rec.order_partner_id.id)
            ]).mapped('cantidad_restante')
            rec.saldo_pedido_abierto = sum(qty_restante)

    def get_lineas(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Líneas de requerimiento',
            'view_mode': 'tree',
            'res_model': 'requisito.compra.linea',
            'domain': [
                ('requisito_compra_rel', '=', self.id),
            ],
            'context': "{'create': False}"
        }

    def get_reporte_req_inventario(self):
        idExternoReporte = 'kanban.reporte_de_requisito_de_compra'
        pdf = self.env.ref(idExternoReporte).sudo().render_qweb_pdf([self.id])[0]
        wiz = self.env['pdf.report.requisito.compra'].create({
            'requisito_compra_id': self.id
        })
        wiz.pdfReporte = base64.encodestring(pdf)
        view = self.env.ref('kanban.view_pdf_report_requisito_compra')
        return {
            'name': _('Requerimiento de inventario'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'pdf.report.requisito.compra',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }
    