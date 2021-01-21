from odoo import _,fields, api,models
from odoo.models import TransientModel
import datetime, time
from odoo.exceptions import UserError,RedirectWarning
from odoo.tools.float_utils import float_compare
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from pdf2image import convert_from_path, convert_from_bytes
import os
import re
from PyPDF2 import PdfFileMerger, PdfFileReader,PdfFileWriter
from io import BytesIO as StringIO
import base64
import datetime
from odoo.tools.mimetypes import guess_mimetype
import logging, ast
from odoo.tools import config, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
_logger = logging.getLogger(__name__)

try:
    import xlrd
    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None

try:
    from . import odf_ods_reader
except ImportError:
    odf_ods_reader = None

FILE_TYPE_DICT = {
    'text/csv': ('csv', True, None),
    'application/vnd.ms-excel': ('xls', xlrd, 'xlrd'),
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ('xlsx', xlsx, 'xlrd >= 1.0.0'),
    'application/vnd.oasis.opendocument.spreadsheet': ('ods', odf_ods_reader, 'odfpy')
}
EXTENSIONS = {
    '.' + ext: handler
    for mime, (ext, handler, req) in FILE_TYPE_DICT.items()
}

class pickingDesasignar(TransientModel):
    _name='picking.desasignar'
    _description='desasignar series'
    solicitud=fields.Many2one('sale.order')

    def confirm(self):
        p=self.solicitud.picking_ids.mapped('state')
        if('done' in p):
            self.ensure_one()
            action_id = self.env.ref('stock.act_stock_return_picking')
            if(self.solicitud.id):
                pi=self.solicitud.picking_ids.filtered(lambda x:x.date_done!=False and x.state=='done').sorted(key='date_done', reverse=True)
                if(pi!=[]):
                    w=self.env['stock.return.picking'].create({'picking_id':pi[0].id,'location_id':12})
                    view=self.env.ref('stock.view_stock_return_picking_form')
                    for m in pi[0].move_ids_without_package:
                        self.env['stock.return.picking.line'].create({'wizard_id':w.id,'product_id':m.product_id.id,'move_id':m.id,'quantity':m.product_uom_qty})
                self.solicitud.write({'state':'sale','x_studio_series_retiro':False})
                self.env.cr.execute("delete stock_picking where origin='"+str(self.solicitud.name)+"';")
            return {
                    'name': _('Ingreso Series Almacen'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'stock.return.picking',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_id':w.id,
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target':'new'
                }

    @api.onchange('solicitud')
    def validacion(self):
        if(self.solicitud.id):
            p=self.solicitud.picking_ids.mapped('state')
            if('done' in p):
                mensajeCuerpo='Solicitud con Movimientos de almacen al confirmar se generara una devolucion al almacen'
                mensajeTitulo = "Alerta!!!"
                warning = {'title': _(mensajeTitulo)
                        , 'message': _(mensajeCuerpo),
                }
                return {'warning': warning}
            else:
                raise UserError(_("Solicitud sin Movimientos de almacen"))


