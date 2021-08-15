# -*- coding: utf-8 -*-
{
    'name': "orden_abierta",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Versión 1.0
    """,

    'author': "Marco Antonio Mandujano Hernandez",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sale',
        'product',
        'stock'
    ],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/sale_order_line.xml',
        'views/product_template.xml',
        'views/sale_order_directa.xml',
        'views/stock_picking_views.xml',
        'views/pedido_directo_views.xml',
        'wizard/sale_order_directa_view.xml',
        'wizard/pdf_report_view.xml',
        'wizard/pedido_abierto_view.xml',
        'report/reportes.xml',
        'report/lista_empaques.xml',
        'data/data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
