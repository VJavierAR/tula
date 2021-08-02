# -*- coding: utf-8 -*-
from odoo import fields, models, api,_
from odoo.exceptions import UserError
from odoo import exceptions
import logging, ast
_logger = logging.getLogger(__name__)


class OrdenAbiertaToDirecta(models.TransientModel):
    _name = 'orden.abierta.to.directa'
    _description = 'Genera orden directa con base a ordenes abiertas'

    def _default_order_line_ids(self):
        return self.env['sale.order.line'].browse(
            self.env.context.get('active_ids'))

    order_line_ids = fields.Many2many(
        string='Ordenes',
        comodel_name="sale.order.line",
        default=lambda self: self._default_order_line_ids(),
        help="",
    )

    def generar_orden(self):
        sale_directa = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id,
            'picking_policy': self.picking_policy,
            'date_order': self.date_order,
            'payment_term_id': self.payment_term_id.id
        })
        id_sale_directa = sale_directa.id
        for line in self.order_line_ids:
            if (line.confirma_venta_directa or not line.fecha_programada) and not line.linea_confirmada:
                linea_generada = line.dup_line_to_order(order_id=id_sale_directa)
                line.linea_confirmada = True
                linea_generada.linea_confirmada = True

        if len(sale_directa.order_line) == 0:
            sale_directa.unlink()
            display_msg = "No se genero orden directa al no tener lineas que confirmar"
            # self.message_post(body=display_msg)
            wiz = self.env['sale.order.alerta'].create({'mensaje': display_msg})
            view = self.env.ref('orden_abierta.sale_order_alerta_view')
            return {
                'name': _(mensajeTitulo),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sale.order.alerta',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }
        else:
            display_msg = "Se genero orden directa con las líneas seleccionadas: <br/>Orden generada: " + sale_directa.name
            # self.message_post(body=display_msg)
            sale_directa.action_confirm()
            for linea in self.order_line_ids:
                linea.order_id.message_post(body=display_msg)
                confirmadas = linea.order_id.mapped('order_line.linea_confirmada')
                if False not in confirmadas:
                    linea.order_id.state = 'sale'

            wiz = self.env['sale.order.alerta'].create({'mensaje': display_msg})
            view = self.env.ref('orden_abierta.sale_order_alerta_view')
            return {
                'name': _(mensajeTitulo),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sale.order.alerta',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }


class Alerta(models.TransientModel):
    _name = 'sale.order.alerta'
    _description = 'Alerta'

    mensaje = fields.Text(
        string='Mensaje'
    )
