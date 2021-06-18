from odoo import models
import logging, ast
import datetime, time
import xlsxwriter
import pytz
_logger = logging.getLogger(__name__)

class MovimientosXlsx(models.AbstractModel):
    _name = 'report.libro.compras'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, account):
        i=2
        d=[]
        merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'blue'})
        report_name = 'Libro de Compras'
        bold = workbook.add_format({'bold': True})
        sheet = workbook.add_worksheet('Libro de Compras')
        sheet.merge_range('A1:R1', 'Libro de Compras', merge_format)
        for obj in account:
            sheet.write(i, 0, str(i-1), bold)
            sheet.write(i, 1, obj.date.strftime("%Y/%m/%d"), bold)
            #sheet.write(i, 2, obj.invoice_doc_serie, bold)
            #sheet.write(i, 3, obj.invoice_doc_number, bold)
            sheet.write(i, 2, '', bold)
            sheet.write(i, 3, '', bold)
            sheet.write(i, 4, obj.partner_id.vat, bold)
            sheet.write(i, 5, obj.partner_id.name, bold)
            sheet.write(i, 6, obj.amount_untaxed if(obj.tipo=='1') else 0, bold)
            sheet.write(i, 7, obj.amount_untaxed if(obj.tipo=='2') else 0, bold)
            sheet.write(i, 8, obj.amount_untaxed if(obj.tipo=='3') else 0, bold)
            sheet.write(i, 9, obj.amount_untaxed if(obj.tipo=='4') else 0, bold)
            sheet.write(i, 10, obj.amount_untaxed if(obj.tipo=='5') else 0, bold)
            iva=obj.line_ids.filtered(lambda x:x.account_id.code=='112101')
            idp=obj.line_ids.filtered(lambda x:x.account_id.code=='531031')
            sheet.write(i, 11,iva[0].debit if(len(iva)>0) else 0, bold)
            sheet.write(i, 12,idp[0].debit if(len(idp)>0) else 0, bold)
            sheet.write(i, 13, obj.amount_untaxed, bold)
            sheet.write(i, 14, obj.amount_total, bold)
            sheet.write(i, 15, obj.ref, bold)
            i=i+1