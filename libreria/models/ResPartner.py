from odoo import api,models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    editorial_books_ids = fields.One2many(
        'library.book','editorial_id',
        string='Libros publicados'
    )

    autores_book_ids = fields.Many2many(
        'library.book',
        string='Libros del autor',
       # relation='library_book_res_partner_rel'
    )
    count_books = fields.Integer('Número de libros del autor',compute='_compute_count_books')
    @api.depends('autores_book_ids')
    def compute_count_books(self):
        for r in self:
            r.count_books = len(r.autores_book_ids)