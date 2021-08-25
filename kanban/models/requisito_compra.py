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
        comodel_name="res.user",
        string="Solicitado por",
        copy=True,
        store=True
    )
    aprobado_por = fields.Many2one(
        comodel_name="res.user",
        string="Aprobado por",
        store=True,
        copy=True,
    )
    realizado_por = fields.Many2one(
        comodel_name="res.user",
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
        store=True
    )

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('requisito.compra.seq') or 'New'

        result = super(RequisitoCompra, self).create(vals)
        return result

    def cambia_a_por_aprobar(self):
        _logger.info('cambia_a_por_aprobar')
        
    def cambia_a_aprobado(self):
        _logger.info('cambia_a_aprobado')
    
    def cambia_a_rechazado(self):
        _logger.info('cambia_a_rechazado')
    
    def cambia_a_realizado(self):
        _logger.info('cambia_a_realizado')
    
    def cambia_a_reiniciar(self):
        _logger.info('cambia_a_reiniciar')

    def get_num_lineas(self):
        return self.env['requisito.compra.linea'].search_count([
            ('requisito_compra_rel', '=', self.id)
        ])
    
    num_lineas = fields.Integer(
        string="Número de líneas",
        default=lambda self: self.get_num_lineas()
    )

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
    