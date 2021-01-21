from odoo import models
import logging, ast
import datetime, time
import xlsxwriter
import pytz
_logger = logging.getLogger(__name__)

class MovimientosXlsx(models.AbstractModel):
    _name = 'report.requisicion.partner_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        i=2
        d=[]
        if(len(partners)==1 and partners.x_studio_arreglo!='/' and partners.x_studio_arreglo!=False):
            copia=partners
            partners=self.env['stock.move.line'].browse(eval(partners.x_studio_arreglo))
            copia.write({'x_studio_arreglo':'/'})
        merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'blue'})
        report_name = 'Movimientos'
        bold = workbook.add_format({'bold': True})
        sheet = workbook.add_worksheet('Movimientos')
        if(13 in partners.mapped('x_studio_field_aVMhn.id')):
            sheet.merge_range('A1:R1', 'Movimientos de Almacen', merge_format)
            for obj in partners:
                e=[]
                d.append(e)
                # One sheet by partner
                
                #_logger.info('work')
                sheet.write(i, 0, obj.x_studio_field_aVMhn.name, bold)
                sheet.write(i, 1, obj.date.strftime("%Y/%m/%d"), bold)
                sheet.write(i, 2, obj.x_studio_field_3lDS0.name, bold)
                if(obj.picking_id.picking_type_id.code =='incoming'):
                    sheet.write(i, 3, "Entrada", bold)
                if(obj.picking_id.picking_type_id.code !='incoming'):
                    sheet.write(i, 3, "Salida", bold)
                sheet.write(i, 4, obj.product_id.name, bold)
                sheet.write(i, 5, obj.product_id.default_code, bold)
                sheet.write(i, 6, obj.qty_done, bold)
                if(obj.lot_id==False):
                    sheet.write(i, 7, obj.product_id.default_code, bold)
                if(obj.lot_id!=False):
                    sheet.write(i, 7, obj.lot_id.name, bold)
                sheet.write(i, 8, obj.move_id.picking_id.partner_id.parent_id.name if(obj.move_id.picking_id.partner_id) else '', bold)
                sheet.write(i, 9, obj.move_id.picking_id.partner_id.name if(obj.move_id.picking_id.partner_id) else '', bold)
                sheet.write(i, 10, obj.x_studio_comentarios if(obj.x_studio_comentarios) else '', bold)
                if(obj.x_studio_ticket):
                    sheet.write(i,11, str(obj.x_studio_ticket) if(obj.x_studio_ticket) else '', bold)
                if(obj.x_studio_ticket==False):
                    sheet.write(i, 11, str(obj.x_studio_orden_de_venta) if(obj.x_studio_orden_de_venta) else '', bold)
                sheet.write(i, 12, obj.x_studio_field_y5FBs if(obj.x_studio_field_y5FBs!=0) else '', bold)
                sheet.write(i, 13, obj.x_studio_serie_destino_1 if(obj.x_studio_serie_destino_1) else '', bold)            
                sheet.write(i, 14, obj.x_studio_modelo_equipo if(obj.x_studio_modelo_equipo) else '', bold)                 
                sheet.write(i, 15, obj.x_studio_estado_destino if(obj.x_studio_estado_destino) else '', bold)            
                sheet.write(i, 16, obj.x_studio_colonia_destino if(obj.x_studio_colonia_destino) else '', bold)
                user=self.env['stock.picking'].search(['&',['sale_id','=',obj.picking_id.sale_id.id],['location_id','=',obj.x_studio_field_3lDS0.lot_stock_id.id]])
                if(obj.x_studio_coment):
                    sheet.write(i, 17, obj.x_studio_coment, bold)
                if(obj.x_studio_coment==False):
                    sheet.write(i, 17, obj.write_uid.name,bold)
                i=i+1
            #sheet.add_table('A2:R2',{'style': 'Table Style Medium 9','columns': [{'header': 'Categoria'},{'header': 'Fecha'},{'header': 'Almacen'},{'header':'Tipo'},{'header': 'Modelo'},{'header': 'No Parte'},{'header': 'Cantidad'},{'header': 'Serie'},{'header': 'Cliente'},{'header': 'Localidad'},{'header': 'Comentario'},{'header': 'Documento Origen'},{'header': 'Numero'},{'header': 'Serie Destino'},{'header': 'Modelo Destino'},{'header': 'Estado'},{'header': 'Delegación'},{'header': 'Usuario'}]})
            sheet.add_table('A2:R'+str(i),{'style': 'Table Style Medium 9','columns': [{'header': 'Categoria'},{'header': 'Fecha'},{'header': 'Almacen'},{'header':'Tipo'},{'header': 'Modelo'},{'header': 'No Parte'},{'header': 'Cantidad'},{'header': 'Serie'},{'header': 'Cliente'},{'header': 'Localidad'},{'header': 'Comentario'},{'header': 'Documento Origen'},{'header': 'Numero'},{'header': 'Serie Destino'},{'header': 'Modelo Destino'},{'header': 'Estado'},{'header': 'Delegación'},{'header': 'Usuario'}]})
            #sheet.add_table('A2:R'+str(i),{'columns': [{'header': 'Categoria'},{'header': 'Fecha'},{'header': 'Almacen'},{'header':'Tipo'},{'header': 'Modelo'},{'header': 'No Parte'},{'header': 'Cantidad'},{'header': 'Serie'},{'header': 'Cliente'},{'header': 'Localidad'},{'header': 'Comentario'},{'header': 'Documento Origen'},{'header': 'Numero'},{'header': 'Serie Destino'},{'header': 'Modelo Destino'},{'header': 'Estado'},{'header': 'Delegación'},{'header': 'Usuario'}]})

        if(13 not in partners.mapped('x_studio_field_aVMhn.id')):
            sheet.merge_range('A1:Q1', 'Movimientos de Almacen', merge_format)
            for obj in partners:
                e=[]
                d.append(e)
                # One sheet by partner
                
                #_logger.info('work')
                sheet.write(i, 0, obj.x_studio_field_aVMhn.name, bold)
                sheet.write(i, 1, obj.date.strftime("%Y/%m/%d"), bold)
                sheet.write(i, 2, obj.x_studio_field_3lDS0.name, bold)
                if(obj.picking_id.picking_type_id.code =='incoming'):
                    sheet.write(i, 3, "Entrada", bold)
                if(obj.picking_id.picking_type_id.code !='incoming'):
                    sheet.write(i, 3, "Salida", bold)
                sheet.write(i, 4, obj.product_id.name, bold)
                sheet.write(i, 5, obj.product_id.default_code, bold)
                sheet.write(i, 6, obj.qty_done, bold)
                sheet.write(i, 7, obj.move_id.picking_id.partner_id.parent_id.name if(obj.move_id.picking_id.partner_id) else '', bold)
                sheet.write(i, 8, obj.move_id.picking_id.partner_id.name if(obj.move_id.picking_id.partner_id) else '', bold)
                sheet.write(i, 9, obj.x_studio_comentarios if(obj.x_studio_comentarios) else '', bold)
                if(obj.x_studio_ticket):
                    sheet.write(i,10, obj.x_studio_ticket if(obj.x_studio_ticket) else '', bold)
                if(obj.x_studio_ticket==False):
                    sheet.write(i, 10, obj.x_studio_orden_de_venta if(obj.x_studio_orden_de_venta) else '', bold)
                sheet.write(i, 11, obj.x_studio_field_y5FBs if(obj.x_studio_field_y5FBs!=0) else '', bold)
                sheet.write(i, 12, obj.x_studio_serie_destino_1 if(obj.x_studio_serie_destino_1) else '', bold)            
                sheet.write(i, 13, obj.x_studio_modelo_equipo if(obj.x_studio_modelo_equipo) else '', bold)                 
                sheet.write(i, 14, obj.x_studio_estado_destino if(obj.x_studio_estado_destino) else '', bold)            
                sheet.write(i, 15, obj.x_studio_colonia_destino if(obj.x_studio_colonia_destino) else '', bold)
                user=self.env['stock.picking'].search(['&',['sale_id','=',obj.picking_id.sale_id.id],['location_id','=',obj.x_studio_field_3lDS0.lot_stock_id.id]])
                if(obj.x_studio_coment):
                    sheet.write(i, 16, obj.x_studio_coment, bold)
                if(obj.x_studio_coment==False):
                    sheet.write(i, 16, obj.write_uid.name,bold)
                i=i+1
            #sheet.add_table('A2:Q2',{'columns': [{'header': 'Categoria'},{'header': 'Fecha'},{'header': 'Almacen'},{'header':'Tipo'},{'header': 'Modelo'},{'header': 'No Parte'},{'header': 'Cantidad'},{'header': 'Cliente'},{'header': 'Localidad'},{'header': 'Comentario'},{'header': 'Documento Origen'},{'header': 'Numero'},{'header': 'Serie Destino'},{'header': 'Modelo Destino'},{'header': 'Estado'},{'header': 'Delegación'},{'header': 'Usuario'}]})
            sheet.add_table('A2:Q'+str(i),{'columns': [{'header': 'Categoria'},{'header': 'Fecha'},{'header': 'Almacen'},{'header':'Tipo'},{'header': 'Modelo'},{'header': 'No Parte'},{'header': 'Cantidad'},{'header': 'Cliente'},{'header': 'Localidad'},{'header': 'Comentario'},{'header': 'Documento Origen'},{'header': 'Numero'},{'header': 'Serie Destino'},{'header': 'Modelo Destino'},{'header': 'Estado'},{'header': 'Delegación'},{'header': 'Usuario'}]})
        workbook.close()




class ExistenciasXML(models.AbstractModel):
    _name = 'report.existencias.report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, quants):
        if(len(quants)==1 and quants.x_studio_arreglo!='/' and quants.x_studio_arreglo!=False):
            copia=quants
            quants=self.env['stock.quant'].browse(eval(quants.x_studio_arreglo))
            copia.sudo().write({'x_studio_arreglo':'/'})
        t=quants.mapped('lot_id.id')
        i=2
        merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'blue'})
        report_name = 'Existencias'
        bold = workbook.add_format({'bold': True})
        if(t!=[]):
            sheet = workbook.add_worksheet('Existencias Equipos')
            sheet.merge_range('A1:K1', 'Existencias Equipos', merge_format)   
            for obj in quants:
                sheet.write(i, 0, obj.x_studio_almacn.name, bold)
                sheet.write(i, 1, obj.product_id.name, bold)
                sheet.write(i, 2, obj.product_id.default_code, bold)
                sheet.write(i, 3, obj.product_id.description if(obj.product_id.description) else '', bold)
                sheet.write(i, 4, obj.lot_id.name, bold)
                sheet.write(i, 5, obj.lot_id.x_studio_estado, bold)
                sheet.write(i, 6, obj.quantity, bold)
                sheet.write(i, 7, obj.reserved_quantity, bold)
                sheet.write(i, 8, obj.x_studio_field_kUc4x.x_name if(obj.x_studio_field_kUc4x.x_name) else '', bold)
                precio=self.env['purchase.order.line'].sudo().search([['product_id','=',obj.product_id.id]])
                sheet.write(i, 9, precio.sorted(key='id',reverse=True)[0].price_unit if(precio) else obj.product_id.lst_price, bold)
                m=self.env['stock.warehouse.orderpoint'].sudo().search([['location_id','=',obj.location_id.id],['product_id','=',obj.product_id.id]])
                sheet.write(i, 10, m.product_min_qty if(m.id) else 0, bold)
                sheet.write(i, 11, m.product_max_qty if(m.id) else 0, bold)
                i=i+1
            sheet.add_table('A2:K2',{'columns': [{'header': 'Almacen'},{'header': 'Modelo'},{'header': 'No Parte'},{'header':'Descripción'},{'header':'No Serie'},{'header': 'Estado'},{'header': 'Existencia'},{'header': 'Apartados'},{'header': 'Ubicación'},{'header':'Costo'},{'header': 'Minimo'},{'header':'Maximo'}]}) 
            #sheet.add_table('A2:I'+str((i)),{'columns': [{'header': 'Almacen'},{'header': 'Modelo'},{'header': 'No Parte'},{'header':'Descripción'},{'header':'No Serie'},{'header': 'Estado'},{'header': 'Apartados'},{'header': 'Ubicación'},{'header':'Costo'}]}) 
        else:
            sheet = workbook.add_worksheet('Existencias Componentes')
            sheet.merge_range('A1:H1', 'Existencias Componentes', merge_format)   
            for obj in quants:
                sheet.write(i, 0, obj.x_studio_almacn.name, bold)
                sheet.write(i, 1, obj.product_id.name, bold)
                sheet.write(i, 2, obj.product_id.default_code, bold)
                sheet.write(i, 3, obj.product_id.description if(obj.product_id.description) else '', bold)
                sheet.write(i, 4, obj.quantity, bold)
                sheet.write(i, 5, obj.reserved_quantity, bold)
                sheet.write(i, 6, obj.x_studio_field_kUc4x.x_name if(obj.x_studio_field_kUc4x.x_name) else '', bold)
                precio=self.env['purchase.order.line'].sudo().search([['product_id','=',obj.product_id.id]])
                sheet.write(i, 7, precio.sorted(key='id',reverse=True)[0].price_unit if(precio) else obj.product_id.lst_price, bold)
                m=self.env['stock.warehouse.orderpoint'].sudo().search([['location_id','=',obj.location_id.id],['product_id','=',obj.product_id.id]])
                sheet.write(i, 8, m.product_min_qty if(m.id) else 0, bold)
                sheet.write(i, 9, m.product_max_qty if(m.id) else 0, bold)
                i=i+1
            sheet.add_table('A2:J2',{'columns': [{'header': 'Almacen'},{'header': 'Modelo'},{'header': 'No Parte'},{'header':'Descripción'},{'header': 'Existencia'},{'header': 'Apartados'},{'header': 'Ubicación'},{'header':'Costo'},{'header': 'Minimo'},{'header':'Maximo'}]}) 
            #sheet.add_table('A2:H'+str((i)),{'columns': [{'header': 'Almacen'},{'header': 'Modelo'},{'header': 'No Parte'},{'header':'Descripción'},{'header': 'Existencia'},{'header': 'Apartados'},{'header': 'Ubicación'},{'header':'Costo'}]}) 
        workbook.close()


class SolicitudesXlsx(models.AbstractModel):
    _name = 'report.solicitudes.report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, sale):
        i=2
        d=[]
        if(len(sale)==1 and sale.x_studio_arreglo!='/' and sale.x_studio_arreglo!=False):
            copia=sale
            sale=self.env['sale.order'].browse(eval(sale.x_studio_arreglo)).filtered(lambda x:x.x_area_atencion==True) 
            copia.write({'x_studio_arreglo':'/'})
        merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'blue'})
        report_name = 'Solicitudes'
        bold = workbook.add_format({'bold': True})
        sheet = workbook.add_worksheet('Solicitudes')
        sheet.merge_range('A1:P1', 'Solicitudes', merge_format)
        for obj in sale:
            equ=obj.order_line.filtered(lambda x:x.product_id.categ_id.id==13)
            if(len(equ)>1):
                for eq in equ:
                    sheet.write(i, 0, obj.name.replace('SO',''), bold)
                    sheet.write(i, 1, obj.confirmation_date.strftime("%Y/%m/%d"), bold)
                    sheet.write(i, 2, obj.partner_id.name, bold)
                    sheet.write(i, 3, obj.x_studio_localidades, bold)
                    sheet.write(i, 4, obj.warehouse_id.name, bold)
                    sheet.write(i, 5, eq.x_studio_estado if eq.x_studio_estado else '', bold)
                    sheet.write(i, 6, eq.product_id.name, bold)
                    #m=self.env['stock.move.line'].search([['picking_id.sale_id','=',obj.id],['lot_id','=',eq.x_studio_field_9nQhR.id]]).lot_id.name
                    sheet.write(i, 7, str(eq.x_studio_field_9nQhR.name) if(eq.x_studio_field_9nQhR.name) else '', bold)
                    a=obj.order_line.filtered(lambda x:x.product_id.categ_id.id==11).mapped('product_id.name')
                    sheet.write(i, 8, str(a).replace('[','').replace(']','').replace('\'','') if(a!=[]) else '', bold)
                    b=obj.order_line.filtered(lambda x:x.product_id.categ_id.id==5).mapped('product_id.name')
                    sheet.write(i, 9, str(b).replace('[','').replace(']','').replace('\'','') if(b!=[]) else '', bold)
                    sheet.write(i, 10, len(obj.order_line.filtered(lambda x:x.product_id.categ_id.id==13).mapped('product_id.name')), bold)
                    sheet.write(i, 11, len(obj.order_line.filtered(lambda x:x.product_id.categ_id.id!=13).mapped('product_id.name')), bold)
                    sheet.write(i, 12, obj.x_studio_tipo_de_solicitud if(obj.x_studio_tipo_de_solicitud) else '', bold)
                    estado='Autorizada' if(obj.state=='sale') else str(obj.state)
                    sheet.write(i, 13, str(estado)+'/'+str(obj.write_uid.name), bold)
                    sheet.write(i, 14, obj.x_studio_usuario_creacion_1, bold)
                    #sheet.write(i, 15, 'Asignado' if(obj.x_studio_asignado) else 'No Asignado', bold)
                    sheet.write(i, 15, str(obj.note) if(obj.note) else '', bold)
                    sheet.write(i, 16, obj.validity_date.strftime("%Y/%m/%d") if(obj.validity_date) else '', bold)
                    i=i+1
            else:
                sheet.write(i, 0, obj.name.replace('SO',''), bold)
                sheet.write(i, 1, obj.confirmation_date.strftime("%Y/%m/%d") if(obj.confirmation_date) else '', bold)
                sheet.write(i, 2, obj.partner_id.name, bold)
                sheet.write(i, 3, obj.x_studio_localidades, bold)
                sheet.write(i, 4, obj.warehouse_id.name, bold)
                sheet.write(i, 5, equ.x_studio_estado if equ.x_studio_estado else '', bold)
                sheet.write(i, 6, equ.product_id.name, bold)
                #m=self.env['stock.move.line'].search([['picking_id.sale_id','=',obj.id],['lot_id','=',equ.x_studio_field_9nQhR.id]]).lot_id.name
                sheet.write(i, 7, str(equ.x_studio_field_9nQhR.name) if(equ.x_studio_field_9nQhR.id) else '', bold)
                a=obj.order_line.filtered(lambda x:x.product_id.categ_id.id==11).mapped('product_id.name')
                sheet.write(i, 8, str(a).replace('[','').replace(']','').replace('\'','') if(a!=[]) else '', bold)
                b=obj.order_line.filtered(lambda x:x.product_id.categ_id.id==5).mapped('product_id.name')
                sheet.write(i, 9, str(b).replace('[','').replace(']','').replace('\'','') if(b!=[]) else '', bold)
                sheet.write(i, 10, len(obj.order_line.filtered(lambda x:x.product_id.categ_id.id==13).mapped('product_id.name')), bold)
                sheet.write(i, 11, len(obj.order_line.filtered(lambda x:x.product_id.categ_id.id!=13).mapped('product_id.name')), bold)
                sheet.write(i, 12, obj.x_studio_tipo_de_solicitud if(obj.x_studio_tipo_de_solicitud) else '', bold)
                estado='Autorizada' if(obj.state=='sale') else str(obj.state)
                sheet.write(i, 13, str(estado)+'/'+str(obj.write_uid.name), bold)
                sheet.write(i, 14, obj.x_studio_usuario_creacion_1, bold)
                #sheet.write(i, 15, 'Asignado' if(obj.x_studio_asignado) else 'No Asignado', bold)
                sheet.write(i, 15, str(obj.note) if(obj.note) else '', bold)
                sheet.write(i, 16, obj.validity_date.strftime("%Y/%m/%d") if(obj.validity_date) else '', bold)
                i=i+1
        sheet.add_table('A2:P'+str(i),{'columns': [{'header': 'Numero de solicitud'},{'header': 'Fecha'},{'header': 'Cliente'},{'header':'Localidades'},{'header': 'Almacen'},{'header': 'Estado'},{'header': 'Modelo'},{'header': 'No. De serie'},{'header': 'Accesorio'},{'header': 'Toner'},{'header': 'Número de equipos'},{'header': 'Número de componentes'},{'header': 'Tipo'},{'header': 'Status'},{'header': 'Usuario Creación'},{'header': 'Comentarios'},{'header': 'Validez'}]}) 
        #sheet.add_table('A2:Q'+str(i),{'columns': [{'header': 'Numero de solicitud'},{'header': 'Fecha'},{'header': 'Cliente'},{'header':'Localidades'},{'header': 'Almacen'},{'header': 'Estado'},{'header': 'Modelo'},{'header': 'No. De serie'},{'header': 'Accesorio'},{'header': 'Toner'},{'header': 'Número de equipos'},{'header': 'Número de componentes'},{'header': 'Tipo'},{'header': 'Status'},{'header': 'Usuario Creación'},{'header': 'Asignado'},{'header': 'Comentarios'}]}) 
        workbook.close()

class TicketsXlsx(models.AbstractModel):
    _name = 'report.tickets.report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, ticket):
        i=2
        d=[]
        if(len(ticket)==1 and ticket.x_studio_arreglo!='/' and ticket.x_studio_arreglo!=False):
            copia=ticket
            ticket=self.env['helpdesk.ticket'].browse(eval(ticket.x_studio_arreglo)).sorted(key='create_date',reverse=True) 
            copia.write({'x_studio_arreglo':'/'})
        merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'blue'})
        report_name = 'Tickets'
        bold = workbook.add_format({'bold': True})
        sheet = workbook.add_worksheet('Tickets')
        sheet.merge_range('A1:X1', 'Tickets', merge_format)
        for obj in ticket:
            tipo=''
            if obj.x_studio_equipo_por_nmero_de_serie_1:
                tipo='Toner'
            if(obj.x_studio_tipo_de_vale==False):
                tipo=''
            if(len(obj.x_studio_equipo_por_nmero_de_serie_1)==1 or len(obj.x_studio_equipo_por_nmero_de_serie)==1):
                sheet.write(i, 0, obj.x_studio_field_nO7Xg.warehouse_id.name if(obj.x_studio_field_nO7Xg.id) else '', bold)
                sheet.write(i, 1, obj.id, bold)
                sheet.write(i, 2, obj.x_studio_tipo_de_vale if(obj.x_studio_tipo_de_vale) else '', bold)
                #sheet.write(i, 3, obj.create_date.strftime("%Y/%m/%d, %H:%M:%S"), bold)
                sheet.write(i, 3, pytz.utc.localize(obj.create_date, is_dst=None).astimezone(pytz.timezone('America/Mexico_City')).strftime("%Y/%m/%d %H:%M:%S"), bold)
                sheet.write(i, 4, obj.days_difference, bold)
                sheet.write(i, 5, obj.partner_id.name if(obj.partner_id) else '', bold)
                sheet.write(i, 6, obj.x_studio_empresas_relacionadas.name if(obj.x_studio_empresas_relacionadas) else '', bold)
                sheet.write(i, 7, str(obj.x_studio_equipo_por_nmero_de_serie_1.serie.name) if(obj.team_id.id==8) else str(obj.x_studio_equipo_por_nmero_de_serie.name), bold)
                sheet.write(i, 8, str(obj.x_studio_equipo_por_nmero_de_serie_1.serie.product_id.name) if(obj.team_id.id==8) else str(obj.x_studio_equipo_por_nmero_de_serie.product_id.name), bold)
                p=[]
                if(len(obj.x_studio_equipo_por_nmero_de_serie_1)==1):
                    if(obj.x_studio_equipo_por_nmero_de_serie_1.x_studio_cartuchonefro):
                        p.append(obj.x_studio_equipo_por_nmero_de_serie_1.x_studio_cartuchonefro.name)
                    if(obj.x_studio_equipo_por_nmero_de_serie_1.x_studio_cartucho_amarillo):
                        p.append(obj.x_studio_equipo_por_nmero_de_serie_1.x_studio_cartucho_amarillo.name)
                    if(obj.x_studio_equipo_por_nmero_de_serie_1.x_studio_cartucho_cian_1):
                        p.append(obj.x_studio_equipo_por_nmero_de_serie_1.x_studio_cartucho_cian_1.name)
                    if(obj.x_studio_equipo_por_nmero_de_serie_1.x_studio_cartucho_magenta):
                        p.append(obj.x_studio_equipo_por_nmero_de_serie_1.x_studio_cartucho_magenta.name)
                sheet.write(i, 9, str(obj.x_studio_productos.mapped('name')).replace('[\'','').replace('\']','').replace('\'','') if(len(obj.x_studio_equipo_por_nmero_de_serie)==1) else str(p).replace('[\'','').replace('\']','').replace('\'',''), bold)
                sheet.write(i, 10, obj.team_id.name if(obj.team_id.id) else "", bold)
                sheet.write(i, 11,obj.x_studio_empresas_relacionadas.state_id.name if(obj.x_studio_empresas_relacionadas.state_id) else '' , bold)
                sheet.write(i, 12, obj.stage_id.name if(obj.stage_id.id) else '', bold)

                sheet.write(i, 13, str(obj.abiertoPor) if(obj.abiertoPor) else '', bold)
                sheet.write(i, 14, str(obj.primerDiagnosticoUsuario) if(obj.primerDiagnosticoUsuario) else '', bold)

                sheet.write(i, 15, obj.x_studio_ultima_nota if(obj.x_studio_ultima_nota) else '', bold)
                sheet.write(i, 16, pytz.utc.localize(obj.ultimoDiagnosticoFecha, is_dst=None).astimezone(pytz.timezone('America/Mexico_City')).strftime("%Y/%m/%d %H:%M:%S") if (obj.ultimoDiagnosticoFecha) else '', bold)
                sheet.write(i, 17, pytz.utc.localize(obj.resuelto_el, is_dst=None).astimezone(pytz.timezone('America/Mexico_City')).strftime("%Y/%m/%d %H:%M:%S") if (obj.resuelto_el) else '', bold)
                sheet.write(i, 18, obj.x_studio_tecnico if(obj.x_studio_tecnico) else obj.write_uid.name, bold)
                sheet.write(i, 19, str(str(obj.x_studio_empresas_relacionadas.street_name)+" No. Ext. "+str(obj.x_studio_empresas_relacionadas.street_number)+" No. Int. "+str(obj.x_studio_empresas_relacionadas.street_number2)+" ,COL. "+str(obj.x_studio_empresas_relacionadas.l10n_mx_edi_colony)+" "+str(obj.x_studio_empresas_relacionadas.city)+" México, "+str(obj.x_studio_empresas_relacionadas.state_id.name)+"C.P "+str(obj.x_studio_empresas_relacionadas.zip)), bold)
                sheet.write(i, 20, obj.x_studio_nmero_de_ticket_cliente if(obj.x_studio_nmero_de_ticket_cliente) else '', bold)
                sheet.write(i, 21, obj.x_studio_nmero_de_guia_1 if(obj.x_studio_nmero_de_guia_1) else '', bold)
                sheet.write(i, 22, pytz.utc.localize(obj.cerrado_el, is_dst=None).astimezone(pytz.timezone('America/Mexico_City')).strftime("%Y/%m/%d %H:%M:%S") if (obj.cerrado_el) else '', bold)
                sheet.write(i, 23, obj.partner_id.x_studio_ejecutivo.name if (obj.partner_id.x_studio_ejecutivo) else '', bold)
                i=i+1
            if(len(obj.x_studio_equipo_por_nmero_de_serie_1)>1 or len(obj.x_studio_equipo_por_nmero_de_serie)>1):
                series=None
                a=False
                if(len(obj.x_studio_equipo_por_nmero_de_serie_1)>1):
                    series=obj.x_studio_equipo_por_nmero_de_serie_1
                    a=True
                if(len(obj.x_studio_equipo_por_nmero_de_serie)>1):
                    series=obj.x_studio_equipo_por_nmero_de_serie
                p=[]
                for s in series:
                    if(a):
                        if(s.x_studio_cartuchonefro):
                            p.append(s.x_studio_cartuchonefro.name)
                        if(s.x_studio_cartucho_amarillo):
                            p.append(s.x_studio_cartucho_amarillo.name)
                        if(s.x_studio_cartucho_cian_1):
                            p.append(s.x_studio_cartucho_cian_1.name)
                        if(s.x_studio_cartucho_magenta):
                            p.append(s.x_studio_cartucho_magenta.name)
                if(series!=None):
                    sheet.write(i, 0, obj.x_studio_field_nO7Xg.warehouse_id.name if(obj.x_studio_field_nO7Xg.id) else '', bold)
                    sheet.write(i, 1, obj.id, bold)
                    sheet.write(i, 2, obj.x_studio_tipo_de_vale if(obj.x_studio_tipo_de_vale) else '', bold)
                    sheet.write(i, 3, pytz.utc.localize(obj.create_date, is_dst=None).astimezone(pytz.timezone('America/Mexico_City')).strftime("%Y/%m/%d %H:%M:%S"), bold)
                    sheet.write(i, 4, obj.days_difference, bold)
                    sheet.write(i, 5, obj.partner_id.name if(obj.partner_id) else '', bold)
                    sheet.write(i, 6, obj.x_studio_empresas_relacionadas.name if(obj.x_studio_empresas_relacionadas) else '', bold)
                    sheet.write(i, 7, str(series.mapped('serie.name')) if(a) else str(series.mapped('name')), bold)
                    sheet.write(i, 8, str(series.mapped('serie.product_id.name')) if(a) else str(series.mapped('name')), bold)
                    sheet.write(i, 9, str(p) if(a) else str(obj.x_studio_productos.mapped('name')), bold)
                    sheet.write(i, 10, obj.team_id.name if(obj.team_id.id) else "", bold)
                    sheet.write(i, 11,obj.x_studio_empresas_relacionadas.state_id.name if(obj.x_studio_empresas_relacionadas.state_id) else '' , bold)
                    sheet.write(i, 12, obj.stage_id.name if(obj.stage_id.id) else '', bold)

                    sheet.write(i, 13, str(obj.abiertoPor) if(obj.abiertoPor) else '', bold)
                    sheet.write(i, 14, str(obj.primerDiagnosticoUsuario) if(obj.primerDiagnosticoUsuario) else '', bold)

                    sheet.write(i, 15, obj.x_studio_ultima_nota if(obj.x_studio_ultima_nota) else '', bold)
                    sheet.write(i, 16, pytz.utc.localize(obj.ultimoDiagnosticoFecha, is_dst=None).astimezone(pytz.timezone('America/Mexico_City')).strftime("%Y/%m/%d %H:%M:%S") if (obj.ultimoDiagnosticoFecha) else '', bold)
                    sheet.write(i, 17, pytz.utc.localize(obj.resuelto_el, is_dst=None).astimezone(pytz.timezone('America/Mexico_City')).strftime("%Y/%m/%d %H:%M:%S") if (obj.resuelto_el) else '', bold)
                    sheet.write(i, 18, obj.x_studio_tecnico if(obj.x_studio_tecnico) else obj.write_uid.name, bold)
                    sheet.write(i, 19, str(str(obj.x_studio_empresas_relacionadas.street_name)+" No. Ext. "+str(obj.x_studio_empresas_relacionadas.street_number)+" No. Int. "+str(obj.x_studio_empresas_relacionadas.street_number2)+" ,COL. "+str(obj.x_studio_empresas_relacionadas.l10n_mx_edi_colony)+" "+str(obj.x_studio_empresas_relacionadas.city)+" México, "+str(obj.x_studio_empresas_relacionadas.state_id.name)+"C.P "+str(obj.x_studio_empresas_relacionadas.zip)), bold)
                    sheet.write(i, 20, obj.x_studio_nmero_de_ticket_cliente if(obj.x_studio_nmero_de_ticket_cliente) else '', bold)
                    sheet.write(i, 21, obj.x_studio_nmero_de_guia_1 if(obj.x_studio_nmero_de_guia_1) else '', bold)
                    sheet.write(i, 22, pytz.utc.localize(obj.cerrado_el, is_dst=None).astimezone(pytz.timezone('America/Mexico_City')).strftime("%Y/%m/%d %H:%M:%S") if (obj.cerrado_el) else '', bold)
                    sheet.write(i, 23, obj.partner_id.x_studio_ejecutivo.name if (obj.partner_id.x_studio_ejecutivo) else '', bold)
                    i=i+1
                else:
                    sheet.write(i, 0, obj.x_studio_field_nO7Xg.warehouse_id.name if(obj.x_studio_field_nO7Xg.id) else '', bold)
                    sheet.write(i, 1, obj.id, bold)
                    sheet.write(i, 2, obj.x_studio_tipo_de_vale if(obj.x_studio_tipo_de_vale) else '', bold)
                    sheet.write(i, 3, pytz.utc.localize(obj.create_date, is_dst=None).astimezone(pytz.timezone('America/Mexico_City')).strftime("%Y/%m/%d %H:%M:%S"), bold)
                    sheet.write(i, 4, obj.days_difference, bold)
                    sheet.write(i, 5, obj.partner_id.name if(obj.partner_id) else '', bold)
                    sheet.write(i, 6, obj.x_studio_empresas_relacionadas.name if(obj.x_studio_empresas_relacionadas) else '', bold)
                    sheet.write(i, 7, '', bold)
                    sheet.write(i, 8, '', bold)
                    sheet.write(i, 9, '', bold)
                    sheet.write(i, 10, obj.team_id.name, bold)
                    sheet.write(i, 11, obj.x_studio_empresas_relacionadas.state_id.name if(obj.x_studio_empresas_relacionadas.state_id) else '' , bold)
                    sheet.write(i, 12, obj.stage_id.name if(obj.stage_id.id) else '', bold)

                    sheet.write(i, 13, str(obj.abiertoPor) if(obj.abiertoPor) else '', bold)
                    sheet.write(i, 14, str(obj.primerDiagnosticoUsuario) if(obj.primerDiagnosticoUsuario) else '', bold)

                    sheet.write(i, 15, obj.x_studio_ultima_nota if(obj.x_studio_ultima_nota) else '', bold)
                    sheet.write(i, 16, pytz.utc.localize(obj.ultimoDiagnosticoFecha, is_dst=None).astimezone(pytz.timezone('America/Mexico_City')).strftime("%Y/%m/%d %H:%M:%S") if (obj.ultimoDiagnosticoFecha) else '', bold)
                    sheet.write(i, 17, pytz.utc.localize(obj.resuelto_el, is_dst=None).astimezone(pytz.timezone('America/Mexico_City')).strftime("%Y/%m/%d %H:%M:%S") if (obj.resuelto_el) else '', bold)
                    sheet.write(i, 18, obj.x_studio_tecnico if(obj.x_studio_tecnico) else obj.write_uid.name, bold)
                    sheet.write(i, 19, str(str(obj.x_studio_empresas_relacionadas.street_name)+" No. Ext. "+str(obj.x_studio_empresas_relacionadas.street_number)+" No. Int. "+str(obj.x_studio_empresas_relacionadas.street_number2)+" ,COL. "+str(obj.x_studio_empresas_relacionadas.l10n_mx_edi_colony)+" "+str(obj.x_studio_empresas_relacionadas.city)+" México, "+str(obj.x_studio_empresas_relacionadas.state_id.name)+"C.P "+str(obj.x_studio_empresas_relacionadas.zip)), bold)
                    sheet.write(i, 20, obj.x_studio_nmero_de_ticket_cliente if(obj.x_studio_nmero_de_ticket_cliente) else '', bold)
                    sheet.write(i, 21, obj.x_studio_nmero_de_guia_1 if(obj.x_studio_nmero_de_guia_1) else '', bold)
                    sheet.write(i, 22, pytz.utc.localize(obj.cerrado_el, is_dst=None).astimezone(pytz.timezone('America/Mexico_City')).strftime("%Y/%m/%d %H:%M:%S") if (obj.cerrado_el) else '', bold)
                    sheet.write(i, 23, obj.partner_id.x_studio_ejecutivo.name if (obj.partner_id.x_studio_ejecutivo) else '', bold)
                    i=i+1
            if(len(obj.x_studio_equipo_por_nmero_de_serie_1) == 0 and len(obj.x_studio_equipo_por_nmero_de_serie) == 0):
                sheet.write(i, 0, obj.x_studio_field_nO7Xg.warehouse_id.name if(obj.x_studio_field_nO7Xg.id) else '', bold)
                sheet.write(i, 1, obj.id, bold)
                sheet.write(i, 2, obj.x_studio_tipo_de_vale if(obj.x_studio_tipo_de_vale) else '', bold)
                sheet.write(i, 3, pytz.utc.localize(obj.create_date, is_dst=None).astimezone(pytz.timezone('America/Mexico_City')).strftime("%Y/%m/%d %H:%M:%S"), bold)
                sheet.write(i, 4, obj.days_difference, bold)
                sheet.write(i, 5, obj.partner_id.name if(obj.partner_id) else '', bold)
                sheet.write(i, 6, obj.x_studio_empresas_relacionadas.name if(obj.x_studio_empresas_relacionadas) else '', bold)
                sheet.write(i, 7, '', bold)
                sheet.write(i, 8, '', bold)
                sheet.write(i, 9, '', bold)
                sheet.write(i, 10, obj.team_id.name, bold)
                sheet.write(i, 11, obj.x_studio_empresas_relacionadas.state_id.name if(obj.x_studio_empresas_relacionadas.state_id) else '' , bold)
                sheet.write(i, 12, obj.stage_id.name if(obj.stage_id.id) else '', bold)

                sheet.write(i, 13, str(obj.abiertoPor) if(obj.abiertoPor) else '', bold)
                sheet.write(i, 14, str(obj.primerDiagnosticoUsuario) if(obj.primerDiagnosticoUsuario) else '', bold)
                
                sheet.write(i, 15, obj.x_studio_ultima_nota if(obj.x_studio_ultima_nota) else '', bold)
                sheet.write(i, 16, pytz.utc.localize(obj.ultimoDiagnosticoFecha, is_dst=None).astimezone(pytz.timezone('America/Mexico_City')).strftime("%Y/%m/%d %H:%M:%S") if (obj.ultimoDiagnosticoFecha) else '', bold)
                sheet.write(i, 17, pytz.utc.localize(obj.resuelto_el, is_dst=None).astimezone(pytz.timezone('America/Mexico_City')).strftime("%Y/%m/%d %H:%M:%S") if (obj.resuelto_el) else '', bold)
                sheet.write(i, 18, obj.x_studio_tecnico if(obj.x_studio_tecnico) else obj.write_uid.name, bold)
                sheet.write(i, 19, str(str(obj.x_studio_empresas_relacionadas.street_name)+" No. Ext. "+str(obj.x_studio_empresas_relacionadas.street_number)+" No. Int. "+str(obj.x_studio_empresas_relacionadas.street_number2)+" ,COL. "+str(obj.x_studio_empresas_relacionadas.l10n_mx_edi_colony)+" "+str(obj.x_studio_empresas_relacionadas.city)+" México, "+str(obj.x_studio_empresas_relacionadas.state_id.name)+"C.P "+str(obj.x_studio_empresas_relacionadas.zip)), bold)
                sheet.write(i, 20, obj.x_studio_nmero_de_ticket_cliente if(obj.x_studio_nmero_de_ticket_cliente) else '', bold)
                sheet.write(i, 21, obj.x_studio_nmero_de_guia_1 if(obj.x_studio_nmero_de_guia_1) else '', bold)
                sheet.write(i, 22, pytz.utc.localize(obj.cerrado_el, is_dst=None).astimezone(pytz.timezone('America/Mexico_City')).strftime("%Y/%m/%d %H:%M:%S") if (obj.cerrado_el) else '', bold)
                sheet.write(i, 23, obj.partner_id.x_studio_ejecutivo.name if (obj.partner_id.x_studio_ejecutivo) else '', bold)
                i=i+1
        sheet.add_table('A2:X'+str(i),{'style': 'Table Style Medium 9','columns': [{'header': 'Almacen'},{'header': 'Ticket'},{'header': 'Tipo de Reporte'},{'header': 'Fecha'},{'header':'Dias de atraso'},{'header': 'Cliente'},{'header': 'Localidad'},{'header': 'Serie'},{'header': 'Modelo'},{'header': 'Productos'},{'header': 'Area de Atención'},{'header': 'Zona'},{'header': 'Estado'},{'header':'Ticket abierto por'},{'header':'Nota inicial'},{'header': 'Ultima nota'},{'header': 'Fecha nota'},{'header': 'Resuelto el'},{'header': 'Tecnico'},{'header': 'Dirección'},{'header': 'No. Ticket cliente'},{'header':'Guia'},{'header':'Cerrado el'},{'header':'Ejecutivo'}]})
        workbook.close()

class ComprasXlsx(models.AbstractModel):
    _name = 'report.compras.report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, purchase):
        i=2
        d=[]
        if(len(purchase)==1 and purchase.x_studio_arreglo!='/' and purchase.x_studio_arreglo!=False):
            copia=purchase
            compras=self.env['purchase.order'].browse(eval(purchase.x_studio_arreglo)).sorted(key='create_date',reverse=True) 
            copia.write({'x_studio_arreglo':'/'})
        merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'blue'})
        report_name = 'Reporte Pagos'
        bold = workbook.add_format({'bold': True})
        sheet = workbook.add_worksheet('Reporte Pagos')
        sheet.merge_range('A1:O1', 'Reporte Pagos', merge_format)
        for obj in compras:
            sheet.write(i, 0, obj.name if(obj.name) else '', bold)
            sheet.write(i, 1, obj.partner_id.name if(obj.partner_id) else '', bold)
            sheet.write(i, 2, obj.x_studio_rubro if(obj.x_studio_rubro) else '', bold)
            sheet.write(i, 3, obj.x_studio_aplicacin.x_name if(obj.x_studio_aplicacin) else '', bold)            
            sheet.write(i, 4, obj.x_studio_concepto if(obj.x_studio_concepto) else '', bold)
            sheet.write(i, 5, '', bold)
            sheet.write(i, 6, '', bold)
            sheet.write(i, 7, obj.x_studio_notas if(obj.x_studio_notas) else '', bold)
            sheet.write(i, 8, obj.amount_untaxed if(obj.amount_untaxed) else '', bold)
            sheet.write(i, 9, obj.amount_tax if(obj.amount_tax) else '', bold)
            sheet.write(i, 10, obj.amount_total if(obj.amount_total) else '', bold)
            sheet.write(i, 11, 'VERONICA APARICIO' if(obj.x_studio_vernica) else 'CLAUDIA MORENO', bold)
            sheet.write(i, 12, '', bold)
            sheet.write(i, 13, '', bold)
            sheet.write(i, 14, '', bold)
            i=i+1
        sheet.add_table('A2:O'+str(i),{'columns': [{'header': 'NO TRNSFER'},{'header': 'PROVEEDOR'},{'header': 'RUBRO'},{'header':'APLICACIÓN '},{'header': 'CONCEPTO'},{'header': 'UBICACIÓN'},{'header': 'FECHA DE FACTURA'},{'header': 'FACTURA'},{'header': 'IMPORTE'},{'header': 'IVA'},{'header': 'TOTAL MN'},{'header': 'RECIBE PARA PAGO'},{'header': 'FECHA DE PAGO'},{'header': 'BANCO'},{'header': 'REFERENCIA'}]}) 
        workbook.close()  

class RutaXlsx(models.AbstractModel):
    _name = 'report.ruta.report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, ruta):
        i=2
        d=[]
        if(len(ruta)==1 and ruta.arreglo!='/' and ruta.arreglo!=False):
            copia=ruta
            ruta=self.env['creacion.ruta'].browse(eval(ruta.arreglo))
            copia.write({'arreglo':'/'})
        merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'blue'})
        report_name = 'Expedición'
        bold = workbook.add_format({'bold': True})
        sheet = workbook.add_worksheet('Expedición')
        sheet.merge_range('A1:V1', 'Reporte Expedición', merge_format)
        for obj in ruta:
            for orden in obj.ordenes:
                sheet.write(i, 0, obj.name if(obj.name) else '', bold)
                sheet.write(i, 1, obj.create_date.strftime("%Y/%m/%d"), bold)
                sheet.write(i, 2, obj.chofer.name if(obj.chofer) else '', bold)
                sheet.write(i, 3, obj.vehiculo.name if(obj.vehiculo) else '', bold)
                sheet.write(i, 4, obj.zona if(obj.zona) else '', bold)
                sheet.write(i, 5, obj.tipo if(obj.tipo) else '', bold)
                sheet.write(i, 6, obj.estado if(obj.estado) else '', bold)            
                sheet.write(i, 7, orden.x_studio_ticket if(orden.x_studio_ticket) else '', bold)
                sheet.write(i, 8, orden.origin if(orden.origin) else '', bold)
                sheet.write(i, 9, len(orden.move_ids_without_package), bold)
                sheet.write(i, 10, str(orden.mapped('move_ids_without_package.product_id.name')), bold)
                sheet.write(i, 11, orden.partner_id.parent_id.name if(orden.partner_id.parent_id.name) else '', bold)
                sheet.write(i, 12, orden.partner_id.name if(orden.partner_id.name) else '', bold)
                sheet.write(i, 13, orden.partner_id.street_name if(orden.partner_id.street_name) else '', bold)
                sheet.write(i, 14, orden.partner_id.street_number2 if(orden.partner_id.street_number2) else '', bold)
                sheet.write(i, 15, orden.partner_id.street_number if(orden.partner_id.street_number) else '', bold)
                sheet.write(i, 16, orden.partner_id.l10n_mx_edi_colony if(orden.partner_id.l10n_mx_edi_colony) else '', bold)
                sheet.write(i, 17, orden.partner_id.l10n_mx_edi_locality if(orden.partner_id.l10n_mx_edi_locality) else '', bold)
                sheet.write(i, 18, orden.partner_id.city if(orden.partner_id.city) else '', bold)
                sheet.write(i, 19, orden.partner_id.zip if(orden.partner_id.zip) else '', bold)
                sheet.write(i, 20, orden.sale_id.x_studio_field_RnhKr.name if(orden.sale_id.x_studio_field_RnhKr.name) else '', bold)
                sheet.write(i, 21, orden.sale_id.x_studio_field_RnhKr.phone if(orden.sale_id.x_studio_field_RnhKr.phone) else '', bold)
                i=i+1
        sheet.add_table('A2:V'+str(i),{'columns': [{'header': 'Expedición'},{'header': 'Fecha'},{'header': 'chofer'},{'header': 'vehiculo'},{'header': 'Zona'},{'header':'Tipo'},{'header': 'Estado'},{'header': 'Ticket'},{'header': 'Orden'},{'header': 'Cantidad'},{'header': 'Productos'},{'header': 'Cliente'},{'header': 'Localidad'},{'header': 'Calle'},{'header': 'No exterior'},{'header': 'No Interior'},{'header': 'Colonia'},{'header': 'Delegación'},{'header': 'Ciudad'},{'header': 'C.p'},{'header': 'Contacto'},{'header': 'Telefono'}]}) 
        workbook.close()

class ContactosXlsx(models.AbstractModel):
    _name = 'report.contacto.report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, contacto):
        i=2
        d=[]
        if(len(contacto)==1 and contacto.arreglo!='/' and contacto.arreglo!=False):
            copia=contacto
            contacto=self.env['res.partner'].browse(eval(contacto.arreglo))
            copia.write({'arreglo':'/'})
        merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'blue'})
        report_name = 'Clientes'
        bold = workbook.add_format({'bold': True})
        sheet = workbook.add_worksheet('Clientes')
        sheet.merge_range('A1:H1', 'Reporte Clientes', merge_format)
        for obj in contacto:
            sheet.write(i, 0, obj.name if(obj.name) else '', bold)
            sheet.write(i, 1, obj.email if(obj.email) else '', bold)
            sheet.write(i, 2, obj.phone if(obj.phone) else '', bold)
            sheet.write(i, 3, obj.tipoCliente if(obj.tipoCliente) else '', bold)
            sheet.write(i, 4, obj.x_studio_nivel_del_cliente if(obj.x_studio_nivel_del_cliente) else '', bold)
            sheet.write(i, 5, obj.x_x_studio_cliente__stock_production_lot_count if(obj.x_x_studio_cliente__stock_production_lot_count) else '', bold)
            sheet.write(i, 6, obj.x_studio_vendedor.name if(obj.x_studio_vendedor) else '', bold)
            sheet.write(i, 7, obj.x_studio_ejecutivo.name if(obj.x_studio_ejecutivo) else '', bold)
            i=i+1
        sheet.add_table('A2:H'+str(i),{'columns': [{'header': 'Nombre'},{'header': 'Email'},{'header': 'Telefono'},{'header': 'Tipo de Cliente'},{'header': 'Nivel'},{'header':'No Equipos'},{'header': 'Vendedor'},{'header': 'Ejecutivo Cuenta'}]}) 
        workbook.close()
            






class LotXlsx(models.AbstractModel):
    _name = 'report.lot.report'
    _inherit = 'report.report_xlsx.abstract'


    def generate_xlsx_report(self, workbook, data, lots):
        i=2
        d=[]
        if(len(lots)==1 and lots.x_studio_arreglo!='/' and lots.x_studio_arreglo!=False):
            copia=lots
            lots=self.env['stock.production.lot'].browse(eval(lots.x_studio_arreglo))
            copia.write({'x_studio_arreglo':'/'})
        merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'blue'})
        report_name = 'Base Instalada'
        bold = workbook.add_format({'bold': True})
        sheet = workbook.add_worksheet('Base Instalada')
        sheet.merge_range('A1:X1', 'Base Instalada', merge_format)
        for obj in lots:
            sheet.write(i, 0, obj.servicio.contrato.cliente.name if(obj.servicio) else '', bold)
            sheet.write(i, 1, obj.servicio.contrato.cliente.x_studio_grupo if(obj.servicio) else '', bold)
            rfc=obj.servicio.contrato.cliente.razonSocial
            sheet.write(i, 2, rfc if rfc else '', bold)
            sheet.write(i, 3, obj.x_studio_localidad_2.name if(obj.servicio) else '', bold)            
            sheet.write(i, 4, obj.name, bold)
            sheet.write(i, 5, obj.product_id.name, bold)
            sheet.write(i, 6, '', bold)
            sheet.write(i, 7, 'Arrendamiento' if(obj.servicio) else '', bold)
            sheet.write(i, 8, obj.servicio.contrato.fechaDeInicioDeContrato.strftime("%Y/%m/%d %H:%M:%S") if(obj.servicio.contrato.fechaDeInicioDeContrato) else '', bold)
            sheet.write(i, 9, obj.servicio.contrato.fechaDeFinDeContrato.strftime("%Y/%m/%d %H:%M:%S") if(obj.servicio.contrato.fechaDeFinDeContrato) else '', bold)
            sheet.write(i, 10, obj.servicio.contrato.idTechraRef if(obj.servicio) else '', bold)
            sheet.write(i, 11, obj.servicio.idtec if(obj.servicio) else '', bold)
            sheet.write(i, 12, obj.servicio.contrato.cliente.x_studio_vendedor.name if(obj.servicio) else '', bold)
            sheet.write(i, 13, obj.servicio.contrato.cliente.x_studio_ejecutivo.name if(obj.servicio) else '', bold)
            sheet.write(i, 14, obj.x_studio_localidad_2.street_name if(obj.servicio) else '', bold)
            sheet.write(i, 15, obj.x_studio_localidad_2.street_number2 if(obj.servicio) else '', bold)
            sheet.write(i, 16, obj.x_studio_localidad_2.street_number if(obj.servicio) else '', bold)
            sheet.write(i, 17, obj.x_studio_localidad_2.l10n_mx_edi_colony if(obj.servicio) else '', bold)
            sheet.write(i, 18, obj.x_studio_localidad_2.city if(obj.servicio) else '', bold)
            sheet.write(i, 19, obj.x_studio_localidad_2.state_id.name if(obj.servicio) else '', bold)
            sheet.write(i, 20, obj.x_studio_localidad_2.state_id.name if(obj.servicio) else '', bold)
            sheet.write(i, 21, obj.x_studio_localidad_2.x_studio_field_SqU5B if(obj.servicio) else '', bold)
            sheet.write(i, 22, 'México' if(obj.servicio) else '', bold)
            sheet.write(i, 23, obj.x_studio_localidad_2.zip if(obj.servicio) else '', bold)
            i=i+1
        sheet.add_table('A2:X'+str(i),{'columns': [{'header': 'NombreCliente'},{'header': 'NombreGrupo'},{'header': 'RFCEmisor'},{'header':'Localidad'},{'header': 'NoSerie'},{'header': 'Modelo'},{'header': 'FechaIngresoCliente'},{'header': 'Tipo'},{'header': 'FechaInicioContrato'},{'header': 'FechaTerminoContrato'},{'header': 'Contrato'},{'header': 'Servicio'},{'header': 'EjecutivoCuenta'},{'header': 'EjecutivoAtencionCliente'},{'header': 'Calle'},{'header': 'No Int'},{'header': 'No Ext'},{'header': 'Colonia'},{'header': 'Delegación'},{'header': 'Ciudad'},{'header': 'Estado'},{'header': 'Zona'},{'header': 'Pais'},{'header': 'Codigo Postal'}]}) 
        workbook.close()

class ContactoPendiente(models.AbstractModel):
    _name = 'report.contacto.inactivo.report'
    _inherit = 'report.report_xlsx.abstract'


    def generate_xlsx_report(self, workbook, data, contacto):
        i=2
        d=[]
        if(len(contacto)==1 and contacto.arreglo!='/' and contacto.arreglo!=False):
            copia=contacto
            contacto=self.env['res.partner'].browse(eval(contacto.arreglo))
            copia.write({'arreglo':'/'})
        merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'blue'})
        report_name = 'Contactos Pendiente Inactivo'
        bold = workbook.add_format({'bold': True})
        sheet = workbook.add_worksheet('Contactos Pendiente Inactivo')
        sheet.merge_range('A1:E1', 'Contactos Pendiente Inactivo', merge_format)
        for obj in contacto:
            sheet.write(i, 0, obj.name if(obj.name) else '', bold)
            sheet.write(i, 1, obj.fechaPendienteInactivo.strftime("%Y/%m/%d") if(obj.fechaPendienteInactivo) else '', bold)
            sheet.write(i, 2, obj.x_studio_ejecutivo.name if(obj.x_studio_ejecutivo.id) else '', bold)
            sheet.write(i, 3, obj.x_studio_vendedor.name if(obj.x_studio_vendedor.id) else '', bold)
            facturas=self.env['account.invoice'].search([['origin','!=',False],['partner_id','=',obj.id]])
            adeudo=0
            for f in facturas:
                adeudo=adeudo+f.residual_signed
            sheet.write(i, 4, adeudo, bold)
            i=i+1
        sheet.add_table('A2:E'+str(i),{'columns': [{'header': 'Nombre Cliente'},{'header': 'Fecha'},{'header': 'Ejecutivo'},{'header':'Vendedor'},{'header':'Monto Adeudado'}]}) 
        workbook.close()
  