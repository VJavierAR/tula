from odoo import models
import base64
from odoo import api, fields, models, _, SUPERUSER_ID
import hashlib 


class ResUser(models.Model):
    _inherit = "res.users"
    second_users=fields.One2many('second.user','rel_user')

class SecondUser(models.Model):
    _name='second.user'
    rel_user=fields.Many2one('res.user')
    name=fields.Char('Nombre')
    user=fields.Char('Mail')
    password=fields.Char('Password')
    
    @api.model
    def create(self, vals):
        password=vals['password']
        result = hashlib.md5(password.encode('ascii'))
        r=str(result.hexdigest())
        password_bytes = r.encode('ascii')
        base64_bytes = base64.b64encode(password_bytes)
        base64_message = base64_bytes.decode('ascii')
        vals['password'] = base64_message
        result = super(SecondUser, self).create(vals)
        return result


    @api.multi
    def write(self, vals):
        password=vals['password']
        result = hashlib.md5(password.encode('ascii'))
        r=str(result.hexdigest())
        password_bytes = r.encode('ascii')
        base64_bytes = base64.b64encode(password_bytes)
        base64_message = base64_bytes.decode('ascii')
        vals['password'] = base64_message
        result = super(SecondUser, self).write(vals)
        return result