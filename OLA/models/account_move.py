# -*- coding: utf-8 -*-
from odoo import fields, models, api,_
from odoo.exceptions import UserError,AccessDenied,RedirectWarning
import logging, ast
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit='account.move'

    cambio_no_permitido = fields.Text(
        string='Intento de cambio no permitido',
        compute='_compute_cambio_no_permitido'
    )
    tramite = fields.Char(
        string='Estado Tramite'        
    )

    @api.onchange('invoice_payment_term_id', 'invoice_line_ids', 'amount_total')
    def cambio_no_permitido(self):
        #_logger.info("self._origin: " + str(self._origin) + " self._origin.id: " + str(self._origin.id))
        #if self._origin.id:
        #[('type', '=', 'out_invoice')]
        simbolo_moneda = "₡"
        if self.company_id.id:
            simbolo_moneda = str(self.company_id.currency_id.symbol)
        if self.type and self.type == 'out_invoice':
            termino_antes = self._origin.invoice_payment_term_id.name
            termino_despues = self.invoice_payment_term_id.name

            #_logger.info("termino_antes: " + str(termino_antes) + " termino_despues: " + str(termino_despues))

            id_usuario_login = self._uid

            usuarios_con_permisos = self.env['res.groups'].sudo().search(
                [
                    ("name", "=", "Confirma pedido de venta que excede límite de crédito")
                ]
            ).mapped('users').mapped('id')
            #_logger.info("usuarios_con_permisos: " + str(usuarios_con_permisos))
            if not id_usuario_login in usuarios_con_permisos:
                raise AccessDenied(_("No tiene los permisos para realizar el cambio de \"terminos de pago\" o \"precios de productos\"."))
            else:
                total = self.amount_residual_signed
                limite_de_credito = self.partner_id.limite_credito
                limite_de_credito_conglomerado = self.partner_id.limite_credito_conglomerado

                state_facturas_no_pagadas = ['posted']

                title = "Alertas: "
                message = """Mensajes: \n"""

                genero_alertas = False

                # Caso en que excede el limite de credito las facturas no pagadas
                facturas_no_pagadas = self.env['account.move'].search(
                    [
                        ('type', '=', 'out_invoice'),
                        ("invoice_payment_state", "=", "not_paid"),
                        ("state", "in", state_facturas_no_pagadas),
                        ("partner_id", "=", self.partner_id.id),
                        ("id", "!=", self._origin.id)
                    ]
                )
                #_logger.info("facturas_no_pagadas_limite_de_credito_unico: ")
                #_logger.info(facturas_no_pagadas)
                total_de_facturas_no_pagadas = 0
                if facturas_no_pagadas:
                    for factura_no_pagada in facturas_no_pagadas:
                        total_de_facturas_no_pagadas += factura_no_pagada.amount_residual_signed

                total_con_facturas = total + total_de_facturas_no_pagadas
                #total_con_facturas = total_de_facturas_no_pagadas
                #_logger.info(
                #    "total_con_facturas: " + str(total_con_facturas) + " > limite_de_credito:" + str(limite_de_credito))
                if total_con_facturas > limite_de_credito:
                    title = title + "Límite de crédito excedido. | "
                    message = message + """Se excedio el límite de crédito por facturas no pagadas: \n
                    Límite de crédito: """ + simbolo_moneda + str(limite_de_credito) + """\n
                    Costo total de factura actual: """ + simbolo_moneda + str(total) + """\n
                    Costo total en facturas no pagadas: """ + simbolo_moneda + str(total_de_facturas_no_pagadas) + """\n
                    Suma total: """ + simbolo_moneda + str(total_con_facturas) + """\n
                    Facturas no pagadas: """ + str(facturas_no_pagadas.mapped('name')) + """\n
                    """.rstrip() + "\n\n"
                    genero_alertas = True

                # Caso en que excede el limite de credito de conglomerado las facturas no pagadas
                facturas_no_pagadas_companies = self.env['account.move'].sudo().search(
                    [
                        ('type', '=', 'out_invoice'),
                        ("invoice_payment_state", "=", "not_paid"),
                        ("state", "in", state_facturas_no_pagadas),
                        ("partner_id", "=", self.partner_id.id),
                        ("id", "!=", self._origin.id)
                    ]
                )
                #_logger.info("facturas_no_pagadas_companies: ")
                #_logger.info(facturas_no_pagadas_companies)
                total_de_facturas_no_pagadas_companies = 0
                if facturas_no_pagadas_companies:
                    for factura_no_pagada in facturas_no_pagadas_companies:
                        total_de_facturas_no_pagadas_companies += factura_no_pagada.amount_residual_signed

                total_con_facturas_companies = total + total_de_facturas_no_pagadas_companies
                #total_con_facturas_companies = total_de_facturas_no_pagadas_companies
                #_logger.info(
                #    "total_con_facturas: " + str(total_con_facturas_companies) + " > limite_de_credito conglomerado:" + str(
                #        limite_de_credito_conglomerado))
                if total_con_facturas_companies > limite_de_credito_conglomerado:
                    title = title + "Límite de crédito de conglomerado excedido. | "
                    message = message + """Se excedio el límite de crédito de conglomerado por facturas no pagadas: \n
                    Límite de crédito de conglomerado: """ + simbolo_moneda + str(limite_de_credito_conglomerado) + """\n
                    Costo total de factura actual: """ + simbolo_moneda + str(total) + """\n
                    Costo total en facturas no pagadas: """ + simbolo_moneda + str(total_de_facturas_no_pagadas_companies) + """\n
                    Suma total: """ + simbolo_moneda + str(total_con_facturas_companies) + """\n
                    Facturas no pagadas: """ + str(facturas_no_pagadas_companies.mapped('name')) + """\n
                    """.rstrip() + "\n\n"
                    genero_alertas = True

                if genero_alertas:
                    #self.bloqueo_limite_credito = True
                    #self.mensaje_limite_de_credito = message
                    return {
                        # 'value': {},
                        'warning': {
                            'title': title,
                            'message': message
                        }
                    }


class ACCOUNT_PAYMENT(models.Model):
    _inherit = 'account.payment'

    def get_num_deposito(self):
        if self.partner_id.numeroUnico:
            return self.partner_id.numeroDeposito

    numeroDeposito = fields.Char(
        string="Número de deposito",
        store=True,
        default=lambda self: self.get_num_deposito()
    )

    numeroUnico = fields.Boolean(
        string="Número único",
        store=True,
        related="partner_id.numeroUnico"
    )

    def confirmar(self):
        if not self.numeroUnico and self.numeroDeposito:
            existe = self.env['account.payment'].search(
                [
                    ('numeroDeposito', '=', self.numeroDeposito),
                    ('partner_id', '=', self.partner_id.id)
                ]
            )
            if existe:
                return
        self.post()


