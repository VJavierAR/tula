from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    editorial_books_ids = fields.One2many(
        'library.book','editorial_id',
        string='Libros publicados'
    )

    autores_book_ids = fields.Many2many(
        'library.book',
        string='Libros del autor',
        relation='library_book_res_partner_rel'
    )

