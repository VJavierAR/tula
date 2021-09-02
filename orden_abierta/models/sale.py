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

estados_glob = [
            ('draft', 'Borrador'),
            ('sent', 'Presupuesto enviado'),
            ('sale', 'Pedido de venta'),
            ('cancel', 'Cancelada'),
            ('orden abierta', 'orden abierta')
        ]


class SaleOrderOrdenAbierta(models.Model):
    _inherit = 'sale.order'
    _description = 'Orden abierta'

    es_orden_abierta = fields.Boolean(
        string="¿Es orden abierta?"
    )

    def _default_state(self):
        return estados_glob

    state = fields.Selection(
        # selection=lambda self: self._default_state(),
        selection_add=[('borrador_pedido_abierto', 'Borrador')]
    )
    pedido_abierto_origen = fields.Many2one(
        comodel_name="pedido.abierto",
        string="Pedido abierto origen",
        required=False
    )
    pedidos_abiertos_origen = fields.Char(
        string="Pedidos abiertos origen",
        required=False,
        store=True
    )
    active = fields.Boolean(
        string="Activo",
        default=True
    )
    pedido_cliente = fields.Char(
        string="Pedido cliente",
        store=True,
        help="Actualiza el dato pedido cliente de todas las lineas de pedido"
    )
    creado_por_pedido_abierto = fields.Boolean(
        string="Creado por pedido abierto",
        default=False,
        store=True
    )
    horario_de_entrega = fields.Datetime(
        string="Horario de entrega",
        related="partner_id.horario_de_entrega"
    )
    """
    reservas = fields.One2many(
        comodel_name='sale.order.reservas',
        inverse_name='sale_id',
        string='Reservas'
    )
    """

    @api.depends('order_line', 'order_line.price_total', 'order_line.price_unit', 'order_line.product_uom_qty',
                 'order_line.product_id')
    def _amount_all(self):
        _logger.info("\n\nCambio sale order line")
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax

            _logger.info("\n\namount_untaxed: " + str(amount_untaxed))
            _logger.info("\n\namount_tax: " + str(amount_tax))
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    amount_untaxed = fields.Monetary(string='Base imponible', store=True, readonly=True, compute='_amount_all',
                                     tracking=5)
    amount_tax = fields.Monetary(string='Impuestos', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all', tracking=4)

    @api.model
    def create(self, vals):
        if 'pedido_cliente' in vals and 'order_line' in vals:
            for linea in vals.get('order_line'):
                linea[2]['pedido_cliente'] = vals['pedido_cliente']

        result = super(SaleOrderOrdenAbierta, self).create(vals)
        return result

    def cancelar(self):
        if self.creado_por_pedido_abierto:
            if len(self.order_line.ids) > 0:
                for linea in self.order_line:
                    cantidad_a_regresar = linea.linea_abierta_rel.cantidad_restante + linea.product_uom_qty
                    linea.linea_abierta_rel.write({
                        'cantidad_restante': cantidad_a_regresar
                    })
                    linea.write({'active': False})
            self.write({
                'active': False
            })
        self.action_cancel()

    @api.onchange('pedido_cliente')
    def actualiza_pedido_cliente_en_lienas(self):
        # if rec.pedido_cliente and len(rec.order_line.ids) > 0:
        for linea in self.order_line:
            linea.pedido_cliente = self.pedido_cliente

    @api.onchange('order_line')
    def cambia_order_line(self):
        if self.pedido_cliente:
            for linea in self.order_line:
                linea.update({'pedido_cliente': self.pedido_cliente})


    def conf(self):
        self.action_confirm()
        """
        orden_abierta = self.es_orden_abierta
        conteo_lineas_confirmadas = 0
        if orden_abierta:
            sale_directa = self.env['sale.order'].create({
                'partner_id': self.partner_id.id,
                'company_id': self.company_id.id,
                'picking_policy': self.picking_policy,
                'date_order': self.date_order,
                'payment_term_id': self.payment_term_id.id
            })
            id_sale_directa = sale_directa.id
            for line in self.order_line:
                if (line.confirma_venta_directa or not line.fecha_programada) and not line.linea_confirmada:
                    linea_generada = line.dup_line_to_order(order_id=id_sale_directa)
                    line.linea_confirmada = True
                    linea_generada.linea_confirmada = True
                if line.linea_confirmada:
                    conteo_lineas_confirmadas += 1
            if conteo_lineas_confirmadas == len(self.order_line.ids):
                self.state = 'sale'
            if len(sale_directa.order_line) == 0:
                sale_directa.unlink()
                display_msg = "No se genero orden directa al no tener lineas que confirmar"
                self.message_post(body=display_msg)
            else:
                display_msg = "Se genero orden directa con las líneas: <br/>Orden generada: " + sale_directa.name
                self.message_post(body=display_msg)
                sale_directa.action_confirm()
        else:
            self.action_confirm()
        """


    """
    @api.onchange('order_line')
    def cambian_lineas(self):
        if self.order_line:
            existe_fecha_programada = False
            for linea in self.order_line:
                if linea.fecha_programada:
                    self.es_orden_abierta = True
                    existe_fecha_programada = True
            if existe_fecha_programada:
                self.state = 'orden abierta'
    """

    """
    @api.model
    def create(self, vals):
        existe_fecha_programada = False
        if 'order_line' in vals:
            lineas = vals['order_line']
            for linea in lineas:
                if 'fecha_programada' in linea[2] and linea[2]['fecha_programada']:
                    vals['es_orden_abierta'] = True
                    existe_fecha_programada = True
        if existe_fecha_programada:
            vals['state'] = 'orden abierta'
        result = super(SaleOrderOrdenAbierta, self).create(vals)
        return result
    """

    def cron_orden_abierta(self):
        genero_html = False
        today_date = datetime.today().strftime("%Y-%m-%d")
        today_date = '2021-08-01'
        _logger.info('today_date: ' + str(today_date))
        usuarios_a_notificar = self.env['res.groups'].sudo().search(
            [("name", "=", "Notificaciones de ordenes abiertas")]).mapped('users.id')
        usuarios_a_notificar_correo = self.env['res.groups'].sudo().search(
            [("name", "=", "Notificaciones de ordenes abiertas")]).mapped('users.email')
        estados_no_aprobados = ['draft', 'sent']
        pedidos_de_venta = self.search([
            ('state', 'in', estados_no_aprobados),
            ('es_orden_abierta', '=', True),
        ])

        company_email = ""
        html = "Ordenes abiertas para ser entregadas hoy: "
        for pedido_abierto in pedidos_de_venta:
            company_email = pedido_abierto.company_id.email
            for linea in pedido_abierto.order_line:
                _logger.info("linea.fecha_programada: " + str(linea.fecha_programada) + " today_date: " + str(today_date) + "pedido_abierto: " + pedido_abierto.name)
                if str(linea.fecha_programada) == str(today_date):
                    html += pedido_abierto.name + "<br/>"
                    genero_html = True

        if genero_html:
            _logger.info("listoooooooooooo")
            template_correo = self.env.ref('orden_abierta.notify_orden_abierta_email_template')
            mail = template_correo.generate_email(self.id)
            mail['email_to'] = str(usuarios_a_notificar_correo).replace('[', '').replace(']', '').replace('\'', '')
            mail['body_html'] = html
            mail['email_from'] = company_email
            self.env['mail.mail'].create(mail).send()

    def get_lista_empaque(self):
        idExternoReporte = 'orden_abierta.reporte_de_lista_empaques'
        pdf = self.env.ref(idExternoReporte).sudo().render_qweb_pdf([self.id])[0]
        wiz = self.env['pdf.report'].create({
            'sale_id': self.id
        })
        wiz.pdfReporte = base64.encodestring(pdf)
        view = self.env.ref('orden_abierta.view_pdf_report')
        return {
            'name': _('Lista empaque'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'pdf.report',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }
