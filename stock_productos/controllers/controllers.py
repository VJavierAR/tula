# -*- coding: utf-8 -*-
# from odoo import http


# class StockProductos(http.Controller):
#     @http.route('/stock_productos/stock_productos/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stock_productos/stock_productos/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('stock_productos.listing', {
#             'root': '/stock_productos/stock_productos',
#             'objects': http.request.env['stock_productos.stock_productos'].search([]),
#         })

#     @http.route('/stock_productos/stock_productos/objects/<model("stock_productos.stock_productos"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stock_productos.object', {
#             'object': obj
#         })
