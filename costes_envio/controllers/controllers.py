# -*- coding: utf-8 -*-
# from odoo import http


# class CostesEnvio(http.Controller):
#     @http.route('/costes_envio/costes_envio/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/costes_envio/costes_envio/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('costes_envio.listing', {
#             'root': '/costes_envio/costes_envio',
#             'objects': http.request.env['costes_envio.costes_envio'].search([]),
#         })

#     @http.route('/costes_envio/costes_envio/objects/<model("costes_envio.costes_envio"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('costes_envio.object', {
#             'object': obj
#         })
