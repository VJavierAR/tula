#-*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta
import pytz
import logging, ast
import re

_logger = logging.getLogger(__name__)
months = ("Enero", "Febrero", "Marzo", "Abri", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")


# licitaciones@promed-sa.com / contraseña: jaxpa
class Crm_l(models.Model):
    _inherit = 'crm.lead'
    no_referencia = fields.Char()
    no_acto = fields.Char(string='Número de acto', store=True)
    fecha_acto = fields.Text() # fields.Datetime()
    conexis = fields.Boolean(default=False)
    contacto=fields.Char(string='Contacto Adicional', store=True)
    telefono=fields.Char(string='Teléfono', store=True)
    website_conexis = fields.Char(string='Sitio web', store=True)
    correo_conexis = fields.Char(string='Correo', store=True)
    quincena=fields.Char()

    @api.onchange('description')
    def test(self):
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz)
        _logger.info("user_tz: " + str(user_tz))

        for record in self:
            if record.description:
                d = record.description.splitlines()
                _logger.info("d: " + str(d))
                if 'CONNEXIS' in record.description:
                    
                    regex = re.compile("^Institución contratante ")
                    idxs = [i for i, item in enumerate(d) if re.search(regex, item)]
                    institucion_contratante = d[idxs[0] + 1] if('Institución contratante (' in record.description) else ''
                    #listo1
                    nombre=d[d.index('Objeto Contractual:')+1] if('Objeto Contractual:' in record.description) else ''
                    #listo2
                    filtered_values = list(filter(lambda v: 'Presupuesto:' in v, d))
                    if(len(filtered_values)>0):
                        if('[B./]' not in filtered_values[0]):
                            value=d[d.index('Presupuesto:')+1].replace('[B./]','').replace(',','').replace(' ','') if('Presupuesto:' in record.description) else '0'
                        if('[B./]' in filtered_values[0]):
                            value=filtered_values[0].replace('Presupuesto: ','').replace('[B./]','').replace(',','').replace(' ','') if(len(filtered_values))>0 else 0
                    #value=filtered_values[0].replace('Presupuesto: ','').replace('[B./]','').replace(',','').replace(' ','') if(len(filtered_values))>0 else 0
                    #listo3
                    filtered_values2 = list(filter(lambda v: 'Fecha/Hora de Cierre de recepción de ofertas: ' in v, d))
                    if(len(filtered_values2)>0):
                        date_time_str = filtered_values2[0].replace('Fecha/Hora de Cierre de recepción de ofertas: ','').replace('Hora: ','')
                        # date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S') + timedelta(hours=6)
                        date_time_obj = date_time_str
                        # date_time_acto = pytz.utc.localize(datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')).astimezone(user_tz)
                        # _logger.info("date_time_obj: " + str(date_time_obj))
                        # _logger.info("date_time_acto: " + str(date_time_acto))

                    if len(filtered_values2) == 0:
                        date_time_obj = False

                    #listo4
                    p = d[d.index('No. de Proceso:')+1] if('No. de Proceso:' in record.description) else ''
                    #listo5
                    values3_temp = list(filter(lambda v: 'Contacto Institucional: ' in v, d))
                    filtered_values3 = values3_temp if(len(values3_temp)>0) else list(filter(lambda v: 'Contacto institucional: ' in v, d))
                    if len(filtered_values3) > 0:
                        cad = filtered_values3[0].replace('Contacto Institucional: ','').split('Nombre:')[1].split('Cargo:') if('Cargo:' in filtered_values3[0]) else filtered_values3[0].replace('Contacto Institucional: ','').split('Nombre:')[1].split('Teléfono:')
                        Nombre = cad[0]
                        tem = cad[1].split('Teléfono:') if('Cargo:' in filtered_values3[0]) else cad
                        temp2 = tem[1].split('Correo:')
                        telefono = temp2[0]
                        correo = temp2[1]
                    if len(filtered_values3) == 0:
                        Nombre = ''
                        telefono = ''
                        correo = ''
                    #listo6
                    e = d[d.index('Enlace al sistema de compras oficial:')+1] if('Enlace al sistema de compras oficial:' in record.description) else ''
                    record['name']=nombre
                    record['expected_revenue']=float(value)
                    record['contact_name']=Nombre
                    record['phone']=telefono
                    record['email_from']=correo
                    record['email_cc']=correo
                    record['correo_conexis']=correo
                    record['website']=e
                    record['fecha_acto'] = date_time_obj

                    record['no_referencia']=p
                    record['no_acto'] = p
                    #record['mobile']=telefono
                    record['contacto']=Nombre
                    record['telefono']=telefono
                    record['website_conexis'] = e
                    record['conexis']=True
                    record['source_id']=self.env.ref('crm_l.conexis_id').id
                    record['partner_name'] = institucion_contratante

                if 'PANAMA COMPRA' in record.description:
                    na=list(filter(lambda v: 'Nombre del Acto:' in v, d))
                    name=na[0].split('Nombre del Acto:')[1] if(len(na)>0) else ''
                    pri=list(filter(lambda v: 'Precio Referencia:	B/. ' in v, d))
                    price=float(pri[0].split('Precio Referencia:	B/. ')[1].replace(',','')) if(len(pri)>0) else 0
                    # da=list(filter(lambda v: 'Fecha y Hora de Apertura de Propuestas:	' in v, d))
                    da = list(filter(lambda v: 'Fecha de Publicación:' in v, d))

                    fecha=False
                    if(len(da)>0):
                        Fec = da[0].replace('Fecha y Hora de Apertura de Propuestas:	','').replace('- ','')
                        # fecha = datetime.strptime(Fec, '%d-%m-%Y %I:%M %p') + timedelta(hours=5)
                        fecha = Fec
                        # fecha = datetime.strptime(Fec, '%d-%m-%Y %I:%M %p')
                        # date_time_acto = pytz.utc.localize(fecha).astimezone(user_tz)

                    nu = list(filter(lambda v: 'Número:	' in v, d))
                    numero = nu[0].split('Número:	')[1] if(len(nu) > 0) else ''
                    URL = 'https://www.panamacompra.gob.pa/Inicio/#!/'
                    nom_c = list(filter(lambda v: 'Nombre:	' in v, d))
                    nombre = nom_c[0].split('Nombre:	')[1] if(len(nom_c) > 0) else ''
                    tel = list(filter(lambda v: 'Teléfono:' in v, d))
                    telefono = tel[0].split('Teléfono:')[1] if(len(tel)>0) else ''
                    corr = list(filter(lambda v: 'Correo Electrónico:' in v, d))
                    correo=corr[0].split('Correo Electrónico:')[1] if(len(corr) > 0) else ''

                    entidad = list(filter(lambda v: 'Unidad De Compra:' in v, d))
                    nom_empresa = entidad[0].split('Unidad De Compra:\t')[1] if (len(entidad) > 0) else ''

                    record['name']=name.replace('\t','')
                    record['expected_revenue']=float(price)
                    record['contact_name']=nombre.replace('\t','')
                    record['phone']=telefono.replace('\t','')
                    record['telefono']=telefono.replace('\t','')
                    record['contacto']=nombre.replace('\t','')
                    #record['mobile']=telefono.replace('\t','')
                    record['email_from']=correo.replace('\t','')
                    record['email_cc']=correo.replace('\t','')
                    record['correo_conexis'] = correo.replace('\t','')
                    record['website']=URL
                    record['website_conexis'] = URL
                    record['fecha_acto'] = fecha
                    record['no_referencia']=numero
                    record['no_acto'] = numero
                    record['source_id']=self.env.ref('crm_l.panama_id').id
                    record['conexis'] = True
                    record['partner_name'] = nom_empresa

    @api.onchange('partner_id')
    def cambia_cliente(self):
        if self._origin.email_from:
            self.email_from = self._origin.email_from
        if self._origin.phone:
            self.phone = self._origin.phone
        if self._origin.website:
            self.website = self._origin.website

    def cron_validate_lost(self):
        # user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz)
        # fecha = pytz.utc.localize(datetime.now()).astimezone(user_tz)
        fecha_ultimo_cambio = self._origin.write_date
        fecha = datetime.now()
        if not self.conexis and abs((fecha - self.write_date).days) >= 180:
            display_msg = "Marcado como perdido al exceder 180 días sin cambios.<br/>Fecha de último cambio: " + \
                          str(self._origin.write_date) + "<br/>Fecha en que se marca como perdida: " + \
                          str(fecha.strftime("%m-%d-%Y"))
            self.message_post(body=display_msg)
            self.write({'active': False, 'probability': 0})
            self.env.cr.commit()
            self.env.cr.execute(
                "update crm_lead set write_date = '" + str(fecha_ultimo_cambio) + "' where  id = " + str(
                    self.id) + ";")
            self.env.cr.commit()

        elif self.conexis and abs((fecha - self.write_date).days) >= 15:
            display_msg = "Marcado como perdido al exceder 15 días sin cambios y ser cargada por Connexis o " \
                          "Panamacompra.<br/>Fecha de último cambio: " + str(self._origin.write_date) + \
                          "<br/>Fecha en que se marca como perdida: " + str(fecha.strftime("%m-%d-%Y"))
            self.message_post(body=display_msg)
            self.write({'active': False, 'probability': 0})
            self.env.cr.commit()
            self.env.cr.execute(
                "update crm_lead set write_date = '" + str(fecha_ultimo_cambio) + "' where  id = " + str(
                    self.id) + ";")
            self.env.cr.commit()
    
    def cron_quincena(self):
        d=self.search([['date_deadline', '!=', False]])
        for data in d:
            dia=data.date_deadline.day
            mes=months[data.date_deadline.month-1]
            if(dia>15):
                data.write({'quincena':'2.ª quincena '+str(mes)+' '+str(data.date_deadline.year)})
            else:
                data.write({'quincena':'1.ª quincena '+str(mes)+' '+str(data.date_deadline.year)})

    @api.model 
    def create(self, vals):
        #rec=super(Crm_l,self).create(vals)
        if('date_deadline' in vals):
            _logger.info(vals['date_deadline'])
            if vals['date_deadline']:
                #user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz)
                fecha = datetime.strptime(vals['date_deadline'], '%Y-%m-%d')
                dia=fecha.day
                mes=mes=months[fecha.month-1]
                if(dia>15):
                    vals['quincena']='2.ª quincena '+str(mes)+' '+str(fecha.year)
                else:
                    vals['quincena']='1.ª quincena '+str(mes)+' '+str(fecha.year)
        rec = super(Crm_l, self).create(vals)      
        return rec

    def write(self, values):
        if 'date_deadline' in values:
            _logger.info(values['date_deadline'])
            fecha = datetime.strptime(values['date_deadline'], '%Y-%m-%d')
            dia = fecha.day
            mes = mes=months[fecha.month-1]
            if(dia>15):
                values['quincena'] = '2.ª quincena '+str(mes)+' '+str(fecha.year)
            else:
                values['quincena'] = '1.ª quincena '+str(mes)+' '+str(fecha.year)

        res = super(Crm_l, self).write(values)
        return res

    def cambia_tipo(self, values):
        if self.description:
            d = self.description.splitlines()
            if 'CONNEXIS' in self.description:
                # listo1
                nombre = d[d.index('Objeto Contractual:') + 1] if ('Objeto Contractual:' in self.description) else ''
                # listo2
                filtered_values = list(filter(lambda v: 'Presupuesto:' in v, d))
                if len(filtered_values) > 0:
                    if '[B./]' not in filtered_values[0]:
                        value = d[d.index('Presupuesto:') + 1].replace('[B./]', '').replace(',', '').replace(' ',
                                                                                                             '') if (
                                    'Presupuesto:' in record.description) else '0'
                    if '[B./]' in filtered_values[0]:
                        value = filtered_values[0].replace('Presupuesto: ', '').replace('[B./]', '').replace(',',
                                                                                                             '').replace(
                            ' ', '') if (len(filtered_values)) > 0 else 0

                # listo3
                filtered_values2 = list(filter(lambda v: 'Fecha/Hora de Cierre de recepción de ofertas: ' in v, d))
                if len(filtered_values2) > 0:
                    date_time_str = filtered_values2[0].replace('Fecha/Hora de Cierre de recepción de ofertas: ',
                                                                '').replace('Hora: ', '')
                    date_time_obj = date_time_str

                if len(filtered_values2) == 0:
                    date_time_obj = False

                # listo4
                p = d[d.index('No. de Proceso:') + 1] if ('No. de Proceso:' in self.description) else ''
                # listo5
                values3_temp = list(filter(lambda v: 'Contacto Institucional: ' in v, d))
                filtered_values3 = values3_temp if (len(values3_temp) > 0) else list(
                    filter(lambda v: 'Contacto institucional: ' in v, d))
                if len(filtered_values3) > 0:
                    cad = filtered_values3[0].replace('Contacto Institucional: ', '').split('Nombre:')[1].split(
                        'Cargo:') if ('Cargo:' in filtered_values3[0]) else \
                    filtered_values3[0].replace('Contacto Institucional: ', '').split('Nombre:')[1].split('Teléfono:')
                    Nombre = cad[0]
                    tem = cad[1].split('Teléfono:') if ('Cargo:' in filtered_values3[0]) else cad
                    temp2 = tem[1].split('Correo:')
                    telefono = temp2[0]
                    correo = temp2[1]
                if len(filtered_values3) == 0:
                    Nombre = ''
                    telefono = ''
                    correo = ''
                # listo6
                e = d[d.index('Enlace al sistema de compras oficial:') + 1] if (
                            'Enlace al sistema de compras oficial:' in self.description) else ''
                values['name'] = nombre
                values['expected_revenue'] = float(value)
                values['contact_name'] = Nombre
                values['phone'] = telefono
                values['email_from'] = correo
                values['email_cc'] = correo
                values['correo_conexis'] = correo
                values['website'] = e
                values['fecha_acto'] = date_time_obj

                values['no_referencia'] = p
                values['no_acto'] = p
                # values['mobile']=telefono
                values['contacto'] = Nombre
                values['telefono'] = telefono
                values['website_conexis'] = e
                values['conexis'] = True
                values['source_id'] = self.env.ref('crm_l.conexis_id').id
            if 'PANAMA COMPRA' in self.description:
                na = list(filter(lambda v: 'Nombre del Acto:' in v, d))
                name = na[0].split('Nombre del Acto:')[1] if (len(na) > 0) else ''
                pri = list(filter(lambda v: 'Precio Referencia:	B/. ' in v, d))
                price = float(pri[0].split('Precio Referencia:	B/. ')[1].replace(',', '')) if (len(pri) > 0) else 0
                da = list(filter(lambda v: 'Fecha y Hora de Apertura de Propuestas:	' in v, d))
                fecha = False
                if len(da) > 0:
                    Fec = da[0].replace('Fecha y Hora de Apertura de Propuestas:	', '').replace('- ', '')
                    fecha = Fec

                nu = list(filter(lambda v: 'Número:	' in v, d))
                numero = nu[0].split('Número:	')[1] if (len(nu) > 0) else ''
                URL = 'https://www.panamacompra.gob.pa/Inicio/#!/'
                nom_c = list(filter(lambda v: 'Nombre:	' in v, d))
                nombre = nom_c[0].split('Nombre:	')[1] if (len(nom_c) > 0) else ''
                tel = list(filter(lambda v: 'Teléfono:' in v, d))
                telefono = tel[0].split('Teléfono:')[1] if (len(tel) > 0) else ''
                corr = list(filter(lambda v: 'Correo Electrónico:' in v, d))
                correo = corr[0].split('Correo Electrónico:')[1] if (len(corr) > 0) else ''
                values['name'] = name.replace('\t', '')
                values['expected_revenue'] = float(price)
                values['contact_name'] = nombre.replace('\t', '')
                values['phone'] = telefono.replace('\t', '')
                values['telefono'] = telefono.replace('\t', '')
                values['contacto'] = nombre.replace('\t', '')
                # values['mobile']=telefono.replace('\t','')
                values['email_from'] = correo.replace('\t', '')
                values['email_cc'] = correo.replace('\t', '')
                values['correo_conexis'] = correo.replace('\t', '')
                values['website'] = URL
                values['website_conexis'] = URL
                values['fecha_acto'] = fecha
                values['no_referencia'] = numero
                values['no_acto'] = numero
                values['source_id'] = self.env.ref('crm_l.panama_id').id
                values['conexis'] = True

        return values


class Iniciativa2Oportunidad(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'

    def action_apply(self):
        result = super(Iniciativa2Oportunidad, self).action_apply()
        # _logger.info("result: " + str(result))
        # _logger.info("result.res_id: " + str(result['res_id']))
        id_oportunidad = result['res_id']
        oportunidad = self.env['crm.lead'].search([('id', '=', id_oportunidad)])
        oportunidad.test()
        # _logger.info("oportunidad: " + str(oportunidad))
        return result

