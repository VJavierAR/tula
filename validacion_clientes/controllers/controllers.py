# -*- coding: utf-8 -*-
# from odoo import http


# class ValidacionClientes(http.Controller):
#     @http.route('/validacion_clientes/validacion_clientes/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/validacion_clientes/validacion_clientes/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('validacion_clientes.listing', {
#             'root': '/validacion_clientes/validacion_clientes',
#             'objects': http.request.env['validacion_clientes.validacion_clientes'].search([]),
#         })

#     @http.route('/validacion_clientes/validacion_clientes/objects/<model("validacion_clientes.validacion_clientes"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('validacion_clientes.object', {
#             'object': obj
#         })
