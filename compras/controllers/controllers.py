# -*- coding: utf-8 -*-
# from odoo import http


# class Compras(http.Controller):
#     @http.route('/compras/compras/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/compras/compras/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('compras.listing', {
#             'root': '/compras/compras',
#             'objects': http.request.env['compras.compras'].search([]),
#         })

#     @http.route('/compras/compras/objects/<model("compras.compras"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('compras.object', {
#             'object': obj
#         })
