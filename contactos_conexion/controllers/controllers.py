# -*- coding: utf-8 -*-
# from odoo import http


# class ContactosConexion(http.Controller):
#     @http.route('/contactos_conexion/contactos_conexion/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/contactos_conexion/contactos_conexion/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('contactos_conexion.listing', {
#             'root': '/contactos_conexion/contactos_conexion',
#             'objects': http.request.env['contactos_conexion.contactos_conexion'].search([]),
#         })

#     @http.route('/contactos_conexion/contactos_conexion/objects/<model("contactos_conexion.contactos_conexion"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('contactos_conexion.object', {
#             'object': obj
#         })
