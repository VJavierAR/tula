# -*- coding: utf-8 -*-
{
    'name': "Modulo de cierre de caja",
    'summary': """Modulo de cierre de caja""",
    'description': """Modulo de cierre de caja""",
    'author': "Cesar Lopez Robredo",
    'website': "cesarlopez173@yahoo.com.mx",
    'category': 'Accounting',
    'version': '1.0',
    'depends': ['base', 'account'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/gastos.xml',
        'data/data.xml',
    ],
        'installable': True,
    'application': True,
    'auto_install': False,

}
