# Copyright 2014 Camptocamp SA - Guewen Baconnier
# Copyright 2018 Tecnativa - Vicent Cubells
# Copyright 2019 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'OLA',
    'version': '13.0.1.0.0',
    'author': 'Cesar Lopez Robredo',
    'website': '',
    'license': 'AGPL-3',
    'category': 'Sale',
    'depends': [
        'base',
        'stock',
        'sale',
        'product',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/stock_picking_view.xml',
        'views/product_template_view.xml',
        'views/res_partner_view.xml',
        'views/sale_order_view.xml',
        'views/product_codigos_view.xml',
        'views/sale_order_line_view.xml',
        'wizard/stock_picking_wizard_view.xml',
        'wizard/sale_order_wizard_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
