from odoo import models, fields
#comentario de control
class LibraryBook(models.Model):
    _name = 'library.book'
    _description='library.book'
    name = fields.Char('Title', required=True)
    date_release = fields.Date('Release Date')
    author_ids = fields.Many2many(
        'res.partner',
        string='Authors'
    )
