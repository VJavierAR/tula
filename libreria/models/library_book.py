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
    #por default odoo genera el display name usando el _rec_name
    _rec_name = 'short_name'
    
    name = fields.Char('Titulo', required=True)
    short_name = fields.Char('Titulo corto', required=True, translate=True, index=True)
    date_release = fields.Date('Fecha de lanzamiento')
    notes = fields.Char('Notas internas')
    #Selection al parecer mandas un arreglo de tuplas con el nombre del valor y el string para mostrar
    # 'State' al final es como aparecer el nombre del campo
    state = fields.Selection(
        [('draft','No disponible'),
        ('available','Disponible'),
        ('lost','Perdido')],
        'Estatus',default="draft")
    description = fields.Html('Descripción', sanitize=True, strip_style=False)
    cover = fields.Binary('Portada')
    out_of_print = fields.Boolean('Agotado')
    date_updated = fields.Datetime('Ultima actualización')

    pages = fields.Integer('Número de páginas',
            groups='base.group_user',
            states={'lost':[('readonly',True)]},
            help='Total de páginas del libro', company_dependent=False)
    
    reader_rating = fields.Float('Calificación promedio del lector', digits=(14,4))

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


        
