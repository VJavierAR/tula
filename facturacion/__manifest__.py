# -*- coding: utf-8 -*-
{
    'name': "facturacion",
    'author': 'Gerardo Leyva Teutli',
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [ 
        'base',
        'stock',
        'sale',
        'product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        # 'views/templates.xml',
        'report/reporte.xml',
        'report/reportC.xml',
        'views/account_move_view.xml',
        'views/account_move_mail.xml',
        'wizard/pagos_wizard.xml',
        'views/res_partner_view.xml',
        'data/tramites_sequence.xml',
    ],
    'css': ['static/src/css/ribbon.css'],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'active': False
}
