# -*- coding: utf-8 -*-
{
    'name': "libro_compras",

    'summary': """""",

    'description': """
        Reporte de excel generado en base a compras realizadas
    """,

    'author': "Cesar Lopez Robredo",
    'website': "cesarlopez173@yahoo.com.mx",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': '',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','report_xlsx','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'report/report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
        'installable': True,
    'application': True,
    'auto_install': False,
    'active': False
}
