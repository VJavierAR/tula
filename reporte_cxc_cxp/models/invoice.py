# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api

from functools import lru_cache


class AccountInvoiceReport(models.Model):
    _name = "account.move.report.ola"
    _description = "Reporte de CxC y CxP"
    _auto = False
    #_rec_name = 'account_move_report_ola'
    _order = 'invoice_date_due'

    # ==== Invoice fields ====
    id = fields.Many2one('account.move', readonly=True, string='Factura')
    name = fields.Char('Num. Factura', readonly=True)
    journal_id = fields.Many2one('account.journal', string='Diario', readonly=True)
    company_id = fields.Many2one('res.company', string='Compañia', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Moneda', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Empresa', readonly=True)
    commercial_partner_id = fields.Many2one('res.partner', string='Empresa padre', readonly=True)
    invoice_user_id = fields.Many2one('res.users', string='Vendedor', readonly=True)

    type = fields.Selection([
        ('out_invoice', 'Factura de Cliente'),
        ('in_invoice', 'Factura de proveedor'),
        ('out_refund', 'Factura rectificativa Clientes'),
        ('in_refund', 'Factura rectificativa Proveedor'),
        ], readonly=True)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('posted', 'Abierta/Pendiente'),
        ('cancel', 'Cancelada/Anulada')
        ], string='Estado', readonly=True)
    invoice_payment_state = fields.Selection(selection=[
        ('not_paid', 'Sin pagar'),
        ('in_payment', 'Sin pagar'),
        ('paid', 'Pagada')
    ], string='Estado de pago', readonly=True)

    invoice_date = fields.Date(readonly=True, string="Fecha Factura")
    invoice_date_due = fields.Date(readonly=True, string="Fecha vencimiento")
    invoice_payment_term_id = fields.Many2one('account.payment.term', string='Termino de pago', readonly=True)

    amount_residual = fields.Monetary(string='Monto adeudado', readonly=True, currency_field='currency_id')
    amount_untaxed = fields.Monetary(string='Subtotal', readonly=True, currency_field='currency_id')
    amount_tax = fields.Monetary(string='Impuesto', readonly=True, currency_field='currency_id')
    amount_total = fields.Monetary(string='Total Factura', readonly=True, currency_field='currency_id')
    dias_vencida = fields.Integer(string='Dias Vencida Calculado', readonly=True)
    dias_vencida_mostrar = fields.Char(string='Dias Vencida', readonly=True)

    @api.model
    def _select(self):
        return '''
            SELECT *, 
            CASE WHEN(dias_vencida > 0) 
                THEN 
                    dias_vencida::varchar || ' DÍAS' 
                ELSE 
                    ABS(dias_vencida)::varchar || ' PARA VENCER' 
                END AS dias_vencida_mostrar 
                FROM 
                    (SELECT
                    move.id,
                    move.currency_id,
                    concat(move.ref, ' ', move.name) as name,
                    move.journal_id,
                    move.company_id,
                    move.partner_id,
                    move.commercial_partner_id,
                    move.invoice_user_id,
                    move.type,
                    move.state,
                    move.invoice_payment_state,
                    move.invoice_date,
                    move.invoice_date_due,
                        CASE 
                        WHEN (move.invoice_date_due is null) THEN 
                                now()::date - (move.invoice_date + interval '1 day' *  (select COALESCE(days, 0) from account_payment_term_line aptl where aptl.payment_id=move.invoice_payment_term_id limit 1) )::date
                        ELSE now()::date - move.invoice_date_due 
                        END as dias_vencida, 
                    move.invoice_payment_term_id,
                    move.amount_residual,
                    move.amount_untaxed,
                    move.amount_tax,
                    move.amount_total
                    
                    FROM account_move move
                    
                    WHERE move.type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund') and move.invoice_payment_state != 'paid' and move.state = 'posted') SUBTABLE
        '''

    @api.model
    def _from(self):
        return '''
            FROM account_move move
        '''

    @api.model
    def _where(self):
        return '''
            WHERE move.type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund') and move.invoice_payment_state != 'paid' and move.state = 'posted'
        '''

    @api.model
    def _group_by(self):
        return '''
            GROUP BY
                move.id,
                move.journal_id,
                move.company_id,
                move.currency_id,
                move.partner_id,
                move.name,
                move.state,
                move.type
        '''

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        """
        self.env.cr.execute('''
            CREATE OR REPLACE VIEW %s AS (
                %s %s %s %s
            )
        ''' % (
            self._table, self._select(), self._from(), self._where(), self._group_by()
        ))
        """
        self.env.cr.execute('''
                    CREATE OR REPLACE VIEW %s AS (
                        %s 
                    )
                ''' % (
            self._table, self._select()
        ))