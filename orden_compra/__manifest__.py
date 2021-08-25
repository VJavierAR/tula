# -*- coding: utf-8 -*-
{
    'name': "orden_compra",

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
    'category': 'Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','purchase','stock','OLA','account_invoice_extract',
'account_taxcloud',
'account_accountant',
'account_predictive_bills',
'account_asset',
'account_reports',
'payment','stock_account',],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
