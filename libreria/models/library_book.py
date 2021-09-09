from odoo import models, fields
#comentario de control
class LibraryBook(models.Model):
    _name = 'library.book'
    _description='Library book'
    #Similar to Order by en sql _order regresa los items en un orden especifico segun
    #según algun registro en este caso date_release
    _order = 'date_release desc, name'
    # se usara en lugar de name como registro insignia de la clase 
    #aqui le indicamos a odoo que short_name sera el nombre que se use cuando se invoque el metodo get_name()
    _rec_name = 'short_name'
    
    name = fields.Char('Title', required=True)
    short_name = fields.Char('Short Title', required=True)
    date_release = fields.Date('Release Date')
    author_ids = fields.Many2many(
        'res.partner',
        string='Authors'
    )
    #En general get_name() usa _rec_name para generar el display name.
    #Pero se puede sobre escribir para generar nuestra propia version del display name
    def get_name(self):
        result = []
        for record in self:
            #con "%s (%s)"  % se formatea la string al mas puro estilo de c 
            # cuando haces printf("%s %s") blabla  
            rec_name = "%s (%s)" % (record.name, record.date_release)
            #get_name() tiene que sacar una tupla el id junto con el display name
            result.append((record.id,rec_name))
        return result


        
