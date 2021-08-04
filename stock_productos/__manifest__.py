# -*- coding: utf-8 -*-
{
    'name': "stock_productos",

    'summary': """
        Stock de productos en bodegas""",

    'description': """
        stock de productos en bodegas
    """,

    'author': "Marco Antonio Mandujano Hernandez",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sale'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_product_view.xml',
        'views/stock_location_views.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
