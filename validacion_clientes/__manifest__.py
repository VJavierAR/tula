# -*- coding: utf-8 -*-
{
    'name': "validacion_clientes",

    'summary': """
        Versión 1.0""",

    'description': """
        Doble validación en la creación del cliente: 
        - Los contactos que creen los usuarios de CRM sólo serán visibles para sí mismo y para los usuarios encargados de crear contactos en la Mesa de Ayuda de cada Compañía. 
        - Al guardar el contacto recién creado, se envía un ticket a la Mesa de Ayuda para su aprobación. Si el usuario con los permisos correspondientes decide que este sea visible para el resto de usuarios de la compañía, podrá habilitar una casilla, dando permiso de su visibilidad.
    """,

    'author': "Marco Antonio Mandujano Hernandez",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'crm'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/crm_views.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'auto_install': False,
    'active': False,
}
