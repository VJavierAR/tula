# -*- coding: utf-8 -*-
# from odoo import http


# class CrmL(http.Controller):
#     @http.route('/crm_l/crm_l/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/crm_l/crm_l/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('crm_l.listing', {
#             'root': '/crm_l/crm_l',
#             'objects': http.request.env['crm_l.crm_l'].search([]),
#         })

#     @http.route('/crm_l/crm_l/objects/<model("crm_l.crm_l"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('crm_l.object', {
#             'object': obj
#         })
