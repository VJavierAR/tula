# -*- coding: utf-8 -*-
# from odoo import http


# class OrdenAbierta(http.Controller):
#     @http.route('/orden_abierta/orden_abierta/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/orden_abierta/orden_abierta/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('orden_abierta.listing', {
#             'root': '/orden_abierta/orden_abierta',
#             'objects': http.request.env['orden_abierta.orden_abierta'].search([]),
#         })

#     @http.route('/orden_abierta/orden_abierta/objects/<model("orden_abierta.orden_abierta"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('orden_abierta.object', {
#             'object': obj
#         })
