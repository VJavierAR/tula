
from odoo import api,models,fields 

class LibraryMember(models.Model):
    _name = 'library.member'
    _inherits = {'res.partner':'partner_id'}
    _description = 'library.member'
    partner_id = fields.Many2one(
        'res.partner',
        ondelete='cascade',
        required=True
    )

    date_start = fields.Date('Miembro desde')
    date_end = fields.Date('Membro hasta')
    member_number = fields.Char()
    date_of_bird = fields.Date('Fecha de nacimiento')