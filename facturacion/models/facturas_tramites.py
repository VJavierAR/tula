from odoo import models, fields, api,_
import logging, ast

_logger = logging.getLogger(__name__)


class Tramites(models.Model):
    _name = 'facturas.tramites'

    clientes = fields.Many2one(
        comodel_name='res.partner',
        store=True,
        track_visibility='onchange'
    )

    tramite_file = fields.Many2many(
        comodel_name="ir.attachment",
        relation="m2m_ir_tramite_file_rel",
        column1="m2m_id",
        column2="attachment_id",
        string="Tramite"
    )

    factura = fields.Many2one(
        comodel_name='account.move',
        store=True,
        track_visibility='onchange'
    )

    tramite_seq = fields.Char(
        string='Tramite secuencia',
        related='factura.tramite_seq'
    )
