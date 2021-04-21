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
        'stock',
        'sale',
        'product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking_view.xml',
        'views/product_template_view.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
