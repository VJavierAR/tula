# -*- coding: utf-8 -*-
{
    'name': 'Cambio en formato de factura',
    'author': 'Odoo',
    'category': 'Account',
    'description':
        '''
        ''',
    'depends': ['base', 'account', 'sale', 'purchase', 'cr_electronic_invoice'],
    'data': [
        'views/sale_views.xml',
        'views/account_views.xml',
        'views/res_company_views.xml',
        'report/report_invoice.xml',
    ],
    'installable': True,
}
