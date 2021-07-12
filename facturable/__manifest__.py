# -*- coding: utf-8 -*-
{
    'name': "facturable",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Cesar Lopez Robredo",
    'website': "cesarlopez173@yahoo.com.mx",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale_management','purchase','stock'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/templates.xml',
        'data/data.xml',
        'wizard/sale_report_update.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
        'installable': True,
    'application': True,
    'auto_install': False,
}
