# -*- coding: utf-8 -*-
{
    'name': "kanban",

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
        'contacts',
        'sale',
        'product',
        'stock',
        'purchase',
        'orden_abierta',
        'mail'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/requisito_compra_linea_views.xml',
        'views/requisito_compra_views.xml',
        'views/requisito_compra_menu.xml',
        'views/requisito_compra_transportista_view.xml',
        'views/templates.xml',
        'wizard/pdf_report_view.xml',
        'report/reportes.xml',
        'report/requisito_compra_reporte.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
