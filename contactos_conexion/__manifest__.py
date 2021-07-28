# -*- coding: utf-8 -*-
{
    'name': "contactos_conexion",

    'summary': """
        Versión 1.0
        """,

    'description': """
        Conexión con API NAF.
    """,

    'author': "Marco Antonio Mandujano Hernandez",
    # 'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    # 'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'crm',
        'sale',
        'product',
        'helpdesk',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/filters_security.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/crm_view.xml',
        'views/res_user_view.xml',
        'views/sale_order_view.xml',
        'views/res_partner_view.xml',
        'views/helpdesk_ticket_view.xml',
        'views/res_company_view.xml',
        'wizard/sale_order_wizard_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'auto_install': False,
    'active': False,
}
