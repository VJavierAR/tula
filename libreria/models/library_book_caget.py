from odoo import models,fields, api

#Una gerarquia es cuando un modelo tiene una relacion de uno a muchos consigo mismo y 
#odoo provee una forma de optimizar las consultas a estos modelos por medio del uso de una gerarquia parent_id y child_id
class BookCategory(models.Model):
    _name = 'library.book.category'
    _description='library.book.category'
    #Campos de activacion de la herarquia optimizada de odoo
    _parent_store =  True
    _parent_name = 'parent_id'
    parent_path = fields.Char(index=True)
    name = fields.Char('Categoria')
    description = fields.Text('Descripción')
    parent_id = fields.Many2one(
        'library.book.category',
        string= 'Categoria padre',
        ondelete = 'restrict',
        index = True
    )
    
    child_ids = fields.One2many(
        'library.book.category','parent_id',
        string = 'Categoria hijo'
    )

    #se agrga un metodo para prevenir que relaciones en ciclo
    @api.constrains('parent_id')
    def _check_herarchy(self):
        if not self._check_recursion():
            raise models.ValidationError(
                'Error! no puedes crear categorias recursivas'
        )
    
    def create_category(self):

        new_category = {'name':'Categoria hija 1',
            'description':'Descripcion de categoria hija 1'
        }

        new_category2 = {'name':'Categoria hija 2',
            'description':'Descripcion de categoria hija 2'
        }
        
        parent_cat_value = {
            'name': 'Categoria padre',
            'description':'Descripcion de la categoria',
            'childs_ids': '[
                (0,0,new_category),
                (0,0,new_category2),
                
            ]'
        }
        #Creando el objeto nuevo con sus hijos adentro 
        record = self.env['library.book.category'].create(parent_cat_value)