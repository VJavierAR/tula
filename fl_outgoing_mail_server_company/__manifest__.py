# -*- coding: utf-8 -*-
{
    'name': 'SMTP by Company',
    'version': '13.0.1.0.0',
    'category': 'Tools',
    'summary': 'Configure SMTP outgoing mail server company wise for sending mail from Odoo, SMTP by company, Outgoing SMTP Mail Server Per company, Company wise Outgoing Mail Server, SMTP server per company',
    'description': """
        This module allows configure outgoing mail server for each company,
        Specify outgoing mail server per company,
        Use your own SMTP mail server for sending mail from Odoo.
    """,
    'sequence': 1,
    'author': 'Futurelens',
    'website': 'http://thefuturelens.com',
    'depends': ['base', 'mail'],
    'data': [
        'views/ir_mail_server_view.xml'
    ],
    'qweb': [],
    'css': [],
    'js': [],
    'images': [
        'static/description/banner_mail_server_company.png',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
    'price': 15,
    'currency': 'USD',
}
