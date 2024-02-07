# -*- coding: utf-8 -*-
# from odoo import http


# class Limites(http.Controller):
#     @http.route('/limites/limites/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/limites/limites/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('limites.listing', {
#             'root': '/limites/limites',
#             'objects': http.request.env['limites.limites'].search([]),
#         })

#     @http.route('/limites/limites/objects/<model("limites.limites"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('limites.object', {
#             'object': obj
#         })
