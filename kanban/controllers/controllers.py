# -*- coding: utf-8 -*-
# from odoo import http


# class Kanban(http.Controller):
#     @http.route('/kanban/kanban/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/kanban/kanban/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('kanban.listing', {
#             'root': '/kanban/kanban',
#             'objects': http.request.env['kanban.kanban'].search([]),
#         })

#     @http.route('/kanban/kanban/objects/<model("kanban.kanban"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kanban.object', {
#             'object': obj
#         })
