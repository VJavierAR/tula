#-*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
import logging, ast
_logger = logging.getLogger(__name__)

class crm_l(models.Model):
    _inherit = 'crm.lead'
    no_referencia=fields.Char()
    fecha_acto=fields.Datetime()
    @api.onchange('description')
    def test(self):
        for record in self:
            if record.description:
                d=record.description.splitlines()
                #listo1
                nombre=d[d.index('Objeto Contractual:')+1]
                #listo2
                filtered_values = list(filter(lambda v: 'Presupuesto:' in v, d))
                value=filtered_values[0].replace('Presupuesto: ','').replace('[B./]','').replace(',','').replace(' ','')

                #listo3
                filtered_values2 = list(filter(lambda v: 'Fecha/Hora de Cierre de recepción de ofertas: ' in v, d))
                date_time_str =filtered_values2[0].replace('Fecha/Hora de Cierre de recepción de ofertas: ','').replace('Hora: ','')
                date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')

                #listo4
                p=d[d.index('No. de Proceso:')+1]
                #listo5
                filtered_values3 = list(filter(lambda v: 'Contacto Institucional: ' in v, d))
                cad=filtered_values3[0].replace('Contacto Institucional: ','').split('Nombre:')[1].split('Cargo:')
                Nombre=cad[0]
                tem=cad[1].split('Teléfono:')
                temp2=tem[1].split('Correo:')
                telefono=temp2[0]
                correo=temp2[1]
                #listo6
                e=d[d.index('Enlace al sistema de compras oficial:')+1]
                record['name']=nombre
                record['expected_revenue']=float(value)
                record['contact_name']=Nombre
                record['phone']=telefono
                record['email_from']=correo
                record['website']=e
                record['fecha_acto']=date_time_obj
                record['no_referencia']=p
                
