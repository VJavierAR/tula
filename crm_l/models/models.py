#-*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
import logging, ast
_logger = logging.getLogger(__name__)


class crm_l(models.Model):
    _inherit = 'crm.lead'
    no_referencia = fields.Char()
    fecha_acto = fields.Datetime()
    conexis = fields.Boolean(default=False)

    @api.onchange('description')
    def test(self):
        for record in self:
            if record.description:
                d=record.description.splitlines()
                if('CONNEXIS' in record.description):
                    #listo1
                    nombre=d[d.index('Objeto Contractual:')+1] if('Objeto Contractual:' in record.description) else ''
                    #listo2
                    filtered_values = list(filter(lambda v: 'Presupuesto:' in v, d))
                    value=filtered_values[0].replace('Presupuesto: ','').replace('[B./]','').replace(',','').replace(' ','') if(len(filtered_values))>0 else 0

                    #listo3
                    filtered_values2 = list(filter(lambda v: 'Fecha/Hora de Cierre de recepción de ofertas: ' in v, d))
                    if(len(filtered_values2)>0):
                        date_time_str =filtered_values2[0].replace('Fecha/Hora de Cierre de recepción de ofertas: ','').replace('Hora: ','')
                        date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
                    if(len(filtered_values2)==0):
                        date_time_obj=False
                    #listo4
                    p=d[d.index('No. de Proceso:')+1] if('No. de Proceso:' in record.description) else ''
                    #listo5
                    filtered_values3 = list(filter(lambda v: 'Contacto Institucional: ' in v, d))
                    if(len(filtered_values3)>0):
                        cad=filtered_values3[0].replace('Contacto Institucional: ','').split('Nombre:')[1].split('Cargo:')
                        Nombre=cad[0]
                        tem=cad[1].split('Teléfono:')
                        temp2=tem[1].split('Correo:')
                        telefono=temp2[0]
                        correo=temp2[1]
                    if(len(filtered_values3)==0):
                        Nombre=''
                        telefono=''
                        correo=''
                    #listo6
                    e=d[d.index('Enlace al sistema de compras oficial:')+1] if('Enlace al sistema de compras oficial:' in record.description) else ''
                    record['name']=nombre
                    record['expected_revenue']=float(value)
                    record['contact_name']=Nombre
                    record['phone']=telefono
                    record['email_from']=correo
                    record['email_cc']=correo
                    record['website']=e
                    record['fecha_acto']=date_time_obj
                    record['no_referencia']=p
                    record['mobile']=telefono
                    record['conexis']=True
                if('PANAMA COMPRA' in record.description):
                    na=list(filter(lambda v: 'Nombre del Acto:' in v, d))
                    name=na[0].split('Nombre del Acto:')[1] if(len(na)>0) else ''
                    pri=list(filter(lambda v: 'Precio Referencia:	B/. ' in v, d))
                    price=float(pri[0].split('Precio Referencia:	B/. ')[1].replace(',','')) if(len(pri)>0) else 0
                    da=list(filter(lambda v: 'Fecha y Hora de Apertura de Propuestas:	' in v, d))
                    fecha=False
                    if(len(da)>0):
                        Fec=da[0].replace('Fecha y Hora de Apertura de Propuestas:	','').replace('- ','')
                        fecha=datetime.strptime(Fec, '%d-%m-%Y %I:%M %p')
                    nu=list(filter(lambda v: 'Número:	' in v, d))
                    numero=nu[0].split('Número:	')[1] if(len(nu)>0) else ''
                    URL='https://www.panamacompra.gob.pa/Inicio/#!/'
                    nom_c=list(filter(lambda v: 'Nombre:	' in v, d))
                    nombre=nom_c[0].split('Nombre:	')[1] if(len(nom_c)>0) else ''
                    tel=list(filter(lambda v: 'Teléfono:' in v, d))
                    telefono=tel[0].split('Teléfono:')[1] if(len(tel)>0) else ''
                    corr=list(filter(lambda v: 'Correo Electrónico:' in v, d))
                    correo=corr[0].split('Correo Electrónico:')[1] if(len(corr)>0) else ''
                    record['name']=name.replace('\t','')
                    record['expected_revenue']=float(price)
                    record['contact_name']=nombre.replace('\t','')
                    record['phone']=telefono.replace('\t','')
                    record['mobile']=telefono.replace('\t','')
                    record['email_from']=correo.replace('\t','')
                    record['email_cc']=correo.replace('\t','')
                    record['website']=URL
                    record['fecha_acto']=fecha
                    record['no_referencia']=numero
                    
    @api.onchange('partner_id')
    def cambia_cliente(self):
        if self._origin.email_from:
            self.email_from = self._origin.email_from
        if self._origin.phone:
            self.phone = self._origin.phone
