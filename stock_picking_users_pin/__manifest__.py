# -*- coding: utf-8 -*-
{
    'name': 'Pin de usuarios en inventario',
    'version': '1.0',
    'category': 'Stock',
    'sequence': 1,
    'description': """
    
    """,
    'author': 'Grupo OLA',
    'depends': ['base', 'stock', 'sale'],
    'data': [
        'wizard/stock_picking_wizard_view.xml',
        'views/stock_picking_views.xml',
        'views/res_users_views.xml',
        'views/sale_views.xml',
             ],
    'installable': True,
    'auto_install': False,
}
