from odoo import  api, models, fields
from odoo.exceptions import ValidationError
from datetime import timedelta

#comentario de control3
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

    #Constrains a nivel de base de datos, basicamente son las soportadas por Postgress
    #Se meten en un arreglo de ternas o tuplas de 3 elementos whatever
    _sql_constraints = [
        ('name_uniq','UNIQUE (name)','El titulo del libro debe ser unico'),
        ('paginas_positivas','CHECK(pages>0)','Número de páginas debe ser positivo')
    ] 
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
    #si el valor del campo state=los este registro se volvera read only
    pages = fields.Integer('Número de páginas',
            groups='base.group_user',
            states={'lost':[('readonly',True)]},
            help='Total de páginas del libro', company_dependent=False)
    
    reader_rating = fields.Float('Calificación promedio del lector', digits=(14,4))
    #En configuracion settins en Decimal presicion se agrego la entrada Book Price y aqui se hace uso de ella
    # pero si no exite va a saltar un error
    cost_price = fields.Float(
        'Costo', digits='Book Price'
    )
    currency_id = fields.Many2one(
        'res.currency', string='Currency',default=33
    )
    retail_price = fields.Monetary('Retail Price',
         currency_field='currency_id'
    )
    author_ids = fields.Many2many(
        'res.partner',
        string='Authors'
    )
    # many2one
    editorial_id = fields.Many2one(
        'res.partner',string='Editorial',
        #opcional:
        ondelete='set null',
        context={},
        domain=[]
    )
    #Categoria con la trampa para evitar la recursividad
    categoria_id = fields.Many2one('library.book.category') 

    #Campo computado
    age_days = fields.Float(
        string='Días desde el lanzamiento',
        compute='_compute_age',
        inverse='_inverse_age',
        search='_search_age',
        store=False, #opcional
        compute_sudo=True  #opcional
    )

    #Campo relacionado, con el ser usar el operador punto para ver campos de 
    # otros modelos atravez de la foranykey local usando el operador punto 
    # related  fields son campos computados, usando la bnadera related_sudo
    # se pueden salar los access rights del usuario activo. 
    publisher_city = fields.Char(
        'publiser City',
        related='publisher_id.city',
        readonly=True
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

    #Constrain a nivel server, osea con codigo python
    #Aqui se valida que la fecha de publicación sea en el pasado
    @api.constrains('date_release')
    def _check_date_release(self):
        for record in self:
            #si tiene fecha de publicación se verifica que el release_date sea menor al dia de hoy
            if record.date_release and record.date_release > fields.Date.today():
                raise models.ValidationError('La fecha de publicación debe ser en el pasado')
        
    #Metodo del campo computado age_days
    #Se le mandan los campos que usara en el computo
    #Calcula el numero de dias,meses y años que han pasado desde la fecha de lanzamiento
    @api.depends('date_release')
    def _compute_age(self):
        print("hola _computed_age ----------------")
        today = fields.Date.today()
        for book in self:
            if book.date_release:
                #a delta se le guarda un  Date y cuando se hace delta.days se sustraen solo los dias
                delta = today - book.date_release
                book.age_days = delta.days
            else:
                book.age_days = 0
    #Inverse permite que un campo computado se editable porque actualiza el campo original que generó el calculo
    #calcula la fecha de lanzamiento apartir del campo age_days
    def _inverse_age(self):
        print("hola _inverse_age----------------")
        today = fields.Date.today()
        # filtered se lo aplica a un array 
        for book in self.filtered('date_release'):
            d = today - timedelta(days=book.age_days)
            book.date_release = d

    def _search_age(self,operator,value):
        print("hola _search_age----------------")
        today = fields.Date.today()
        value_days = timedelta(days=value)
        value_date = today - value_days
        #comvert the operator
        #libros con age > value tiene una fecha < value_date
        operator_map = {
            '>':'<','>=':'<=','<':'>','<=':'>=',
        }
        new_op = operator_map.get(operator,operator)
        return [('date_release',new_op,value_date)]

    #Desde odoo 13 existe un cache global que segun optimiza las consultas
    #pero si se actualizan campos que usemos como contexto puede que no se actualizen
    #y que se calculen mal las cosas por eso se usan las anotaciones @api_depends y @api_depends_context
    """
    @api_depends('price')
    @api_depends_context('company_id')
    def _compute_value(self):
        company_id = self.env.context.get('company_id')
        ...
        #other computation
    """