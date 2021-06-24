from odoo import models, fields, api, _
from odoo.tools import email_split, float_is_zero
from odoo.addons.cr_electronic_invoice.models import fe_enums
import re
import random
import phonenumbers

class Gastos2(models.Model):
    _inherit = 'hr.expense'

    def action_move_create2(self):
        '''
        main function that is called when trying to create the accounting entries related to an expense
        '''
        move_group_by_sheet = self._get_account_move_by_sheet()

        move_line_values_by_expense = self._get_account_move_line_values()

        for expense in self:
            company_currency = expense.company_id.currency_id
            different_currency = expense.currency_id != company_currency

            # get the account move of the related sheet
            move = move_group_by_sheet[expense.sheet_id.id]

            # get move line values
            move_line_values = move_line_values_by_expense.get(expense.id)
            move_line_dst = move_line_values[-1]
            total_amount = move_line_dst['debit'] or -move_line_dst['credit']
            total_amount_currency = move_line_dst['amount_currency']

            # create one more move line, a counterline for the total on payable account
            if expense.payment_mode == 'company_account':
                if not expense.sheet_id.bank_journal_id.default_credit_account_id:
                    raise UserError(_("No credit account found for the %s journal, please configure one.") % (
                        expense.sheet_id.bank_journal_id.name))
                journal = expense.sheet_id.bank_journal_id
                # create payment
                payment_methods = journal.outbound_payment_method_ids if total_amount < 0 else journal.inbound_payment_method_ids
                journal_currency = journal.currency_id or journal.company_id.currency_id
                payment = self.env['account.payment'].create({
                    'payment_method_id': payment_methods and payment_methods[0].id or False,
                    'payment_type': 'outbound' if total_amount < 0 else 'inbound',
                    'partner_id': expense.employee_id.address_home_id.commercial_partner_id.id,
                    'partner_type': 'supplier',
                    'type': 'in_invoice',
                    'journal_id': journal.id,
                    'payment_date': expense.date,
                    'state': 'reconciled',
                    'currency_id': expense.currency_id.id if different_currency else journal_currency.id,
                    'amount': abs(total_amount_currency) if different_currency else abs(total_amount),
                    'name': expense.name,
                })
                move_line_dst['payment_id'] = payment.id

            # link move lines to move, and move to expense sheet
            move.write({'line_ids': [(0, 0, line) for line in move_line_values]})
            expense.sheet_id.write({'account_move_id': move.id})

            if expense.payment_mode == 'company_account':
                expense.sheet_id.paid_expense_sheets()

        # post the moves
        #for move in move_group_by_sheet.values():
        #    move.post()
        sheet_env = self.env['hr.expense.sheet']
        for sheet_id, move in move_group_by_sheet.items():
            move.write({'type': 'in_invoice', 'partner_id': sheet_env.browse(sheet_id).supplier_id.id})
            for line in move.invoice_line_ids:
                if not line.product_id:
                    line.exclude_from_invoice_tab = True

        return move_group_by_sheet



class Gastos(models.Model):
    _inherit = 'hr.expense.sheet'


    documento = fields.Binary('Documento')
    documento_fname = fields.Char('Documento')
    tipo_documento = fields.Selection(
        selection=[
                ('CCE', 'Aceptación de comprobante'),
                ('CPCE', 'Aceptación Parcial de comprobante'),
                ('RCE', 'Rechazo de comprobante'),
                ('FEC', 'Factura Electrónica de Compra'),
                ('disabled', 'No generar documento')],
        string="Tipo Comprobante",
        required=False,
        help='Indica el tipo de documento de acuerdo a la '
             'clasificación del Ministerio de Hacienda', default='disabled')
    num_doc_electronico = fields.Char('# doc Electrónico', readonly=True)
    supplier_id = fields.Many2one('res.partner', 'Proveedor')

    def get_clave_hacienda(self, doc, tipo_documento, consecutivo, sucursal_id=1, terminal_id=1, situacion='normal'):

        tipo_doc = fe_enums.TipoDocumento[tipo_documento]

        '''Verificamos si el consecutivo indicado corresponde a un numero'''
        inv_consecutivo = re.sub('[^0-9]', '', consecutivo)
        if len(inv_consecutivo) != 10:
            raise UserError('La numeración debe de tener 10 dígitos')

        '''Verificamos la sucursal y terminal'''
        inv_sucursal = re.sub('[^0-9]', '', str(sucursal_id)).zfill(3)
        inv_terminal = re.sub('[^0-9]', '', str(terminal_id)).zfill(5)

        '''Armamos el consecutivo pues ya tenemos los datos necesarios'''
        consecutivo_mh = inv_sucursal + inv_terminal + tipo_doc + inv_consecutivo

        if not doc.company_id.identification_id:
            raise UserError(
                'Seleccione el tipo de identificación del emisor en el pérfil de la compañía')

        '''Obtenemos el número de identificación del Emisor y lo validamos númericamente'''
        inv_cedula = re.sub('[^0-9]', '', doc.company_id.vat)

        '''Validamos el largo de la cadena númerica de la cédula del emisor'''
        if doc.company_id.identification_id.code == '01' and len(inv_cedula) != 9:
            raise UserError('La Cédula Física del emisor debe de tener 9 dígitos')
        elif doc.company_id.identification_id.code == '02' and len(inv_cedula) != 10:
            raise UserError(
                'La Cédula Jurídica del emisor debe de tener 10 dígitos')
        elif doc.company_id.identification_id.code == '03' and len(inv_cedula) not in (11, 12):
            raise UserError(
                'La identificación DIMEX del emisor debe de tener 11 o 12 dígitos')
        elif doc.company_id.identification_id.code == '04' and len(inv_cedula) != 10:
            raise UserError(
                'La identificación NITE del emisor debe de tener 10 dígitos')

        inv_cedula = str(inv_cedula).zfill(12)

        '''Limitamos la cedula del emisor a 20 caracteres o nos dará error'''
        cedula_emisor = inv_cedula

        '''Validamos la situación del comprobante electrónico'''
        situacion_comprobante = fe_enums.SituacionComprobante.get(situacion)
        if not situacion_comprobante:
            raise UserError(
                'La situación indicada para el comprobante electŕonico es inválida: ' + situacion)

        '''Creamos la fecha para la clave'''
        invoice_date = fields.Date.today()
        dia = str(invoice_date.day).zfill(2)  # [8:10]#'%02d' % now_cr.day,
        mes = str(invoice_date.month).zfill(2)  # [5:7]#'%02d' % now_cr.month,
        anno = str(invoice_date.year)[2:]  # str(now_cr.year)[2:4],
        cur_date = dia + mes + anno

        phone = phonenumbers.parse(doc.company_id.phone,
                                   doc.company_id.country_id and doc.company_id.country_id.code or 'CR')
        codigo_pais = str(phone and phone.country_code or 506)

        '''Creamos un código de seguridad random'''
        codigo_seguridad = str(random.randint(1, 99999999)).zfill(8)

        clave_hacienda = codigo_pais + cur_date + cedula_emisor + \
                         consecutivo_mh + situacion_comprobante + codigo_seguridad

        return {'length': len(clave_hacienda), 'clave': clave_hacienda, 'consecutivo': consecutivo_mh}

    def action_sheet_move_create2(self):
        result = super(Gastos, self).action_sheet_move_create()
        if self.tipo_documento:
            if self.tipo_documento == 'CCE':
                tip_doc = 'CCE' # confirmacion comprobante electronico
                sequence = self.company_id.CCE_sequence_id.next_by_id()
            elif self.tipo_documento == 'CPCE':
                tip_doc = 'CPCE'  # confirmacion parcial comprobante electronico
                sequence = self.company_id.CPCE_sequence_id.next_by_id()
            elif self.tipo_documento == 'RCE':
                tip_doc = 'RCE'  # rechazo comprobante electronico
                sequence = self.company_id.RCE_sequence_id.next_by_id()
            else: #simplificado, factura electronica de compra
                tip_doc = 'FEC'  # Factura Electrónica de Compra
                sequence = self.company_id.FEC_sequence_id.next_by_id()
            self.num_doc_electronico = self.get_clave_hacienda(self, tip_doc, sequence)['clave']
        return result

