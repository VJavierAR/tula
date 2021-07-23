# -*- coding: utf-8 -*-
{
    'name': "Modulo de cierre de caja",
    'summary': """Modulo de cierre de caja""",
    'description': """Modulo de cierre de caja""",
    'author': "Grupo OLA SA",
    'website': "https://grupoola.odoo.com",
    'category': 'general',
    'version': '1.0',
    'depends': ['base', 'account'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/gastos.xml',
        'data/data.xml',
    ],
}
