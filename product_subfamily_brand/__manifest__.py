# -*- coding: utf-8 -*-
{
    'name': 'Subfamilia y Marca en productos',
    'author': 'Odoo',
    'category': 'Stock',
    'description':
        '''
        ''',
    'depends': ['product', 'stock', 'sale', 'account'],
    'data': [
        'views/product_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
