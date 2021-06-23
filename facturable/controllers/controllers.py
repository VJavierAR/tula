# -*- coding: utf-8 -*-
# from odoo import http


# class Facturable(http.Controller):
#     @http.route('/facturable/facturable/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/facturable/facturable/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('facturable.listing', {
#             'root': '/facturable/facturable',
#             'objects': http.request.env['facturable.facturable'].search([]),
#         })

#     @http.route('/facturable/facturable/objects/<model("facturable.facturable"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('facturable.object', {
#             'object': obj
#         })
