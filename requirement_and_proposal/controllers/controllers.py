# -*- coding: utf-8 -*-
# from odoo import http


# class RequirementAndProposal(http.Controller):
#     @http.route('/requirement_and_proposal/requirement_and_proposal/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/requirement_and_proposal/requirement_and_proposal/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('requirement_and_proposal.listing', {
#             'root': '/requirement_and_proposal/requirement_and_proposal',
#             'objects': http.request.env['requirement_and_proposal.requirement_and_proposal'].search([]),
#         })

#     @http.route('/requirement_and_proposal/requirement_and_proposal/objects/<model("requirement_and_proposal.requirement_and_proposal"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('requirement_and_proposal.object', {
#             'object': obj
#         })
