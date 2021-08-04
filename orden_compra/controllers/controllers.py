# -*- coding: utf-8 -*-
# from odoo import http


# class OrdenCompra(http.Controller):
#     @http.route('/orden_compra/orden_compra/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/orden_compra/orden_compra/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('orden_compra.listing', {
#             'root': '/orden_compra/orden_compra',
#             'objects': http.request.env['orden_compra.orden_compra'].search([]),
#         })

#     @http.route('/orden_compra/orden_compra/objects/<model("orden_compra.orden_compra"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('orden_compra.object', {
#             'object': obj
#         })
