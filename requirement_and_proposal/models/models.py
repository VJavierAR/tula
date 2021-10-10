# -*- coding: utf-8 -*-
from odoo import models, fields, api


class RequirementProposal(models.Model):
    _name = 'client.requirement'
    _description = 'Solicitud de requerimiento del cliente'
    name = fields.Char()
    descripcion = fields.Char('Descripción')
    marca = fields.Char('Marca')
    modelo = fields.Char('Modelo')
    cantidad = fields.Float('Cantidad')
    presupuesto = fields.Float('Presupuesto')
    proveedor = fields.Char('Proveedor')
    condicion = fields.Many2one('product.state', string='Condicion')
    completo = fields.Boolean('Completo')
    estado_cliente = fields.Boolean('Estado del cliente')
    estado = fields.Selection([('accepted', 'Aceptado'), ('process', 'En proceso'), ('cancel', 'Cancelado')],
                              string='Estado')
    order_id = fields.Many2one('sale.order')
    lines_proposal = fields.One2many('proposal.purchase', 'rel_id')

    def view_purchase_proposal(self):
        action = self.env.ref('proposal_purchase_action_window').read()[0]
        #form_view = [(self.env.ref('proposal_purchase_list').id, 'tree')]
        lines = self.lines_proposal.mapped('id')
        if lines != []:
            action['domain'] = [('id', 'in', lines)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def create_purchase_proposal(self):
        view = self.env.ref('wizard_proposal_form')
        wiz = self.env['wizard.proposal'].create({'rel_id': self.id})
        return {
        'name': _('Propuesta'),
        'type': 'ir.actions.act_window',
        'view_mode': 'form',
        'res_model': 'wizard.proposal',
        'views': [(view.id, 'form')],
        'view_id': view.id,
        'target': 'new',
        'res_id': wiz.id,
        'context': self.env.context}

class ProductState(models.Model):
    _name = 'product.state'
    name = fields.Char()


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    lines_requirements = fields.One2many('client.requirement', 'order_id')


class ProposalPurchase(models.Model):
    _name = 'proposal.purchase'
    _description = 'Propuesta de Compras'
    name = fields.Char()
    product_id = fields.Many2one('product.product', 'Producto')
    cantidad = fields.Float('Cantidad')
    costo = fields.Float('Costo')
    proveedor = fields.Many2one('res.partner')
    condicion = fields.Many2one('product.state', 'Condicion')
    rel_id = fields.Many2one('client.requirement')


class WizardProposal(models.TransientMode):
    _name = 'wizard.proposal'
    _description = 'Asistente de Propuesta'
    name = fields.Char()
    product_id = fields.Many2one('product.product', 'Producto')
    cantidad = fields.Float('Cantidad')
    costo = fields.Float('Costo')
    proveedor = fields.Many2one('res.partner')
    condicion = fields.Many2one('product.state', 'Condicion')
    rel_id = fields.Many2one('client.requirement')
    detalle = fields.Char(compute='_compute_detalle', string='Detalle')

    def confirm(self):
        self.env['proposal.purchase'].create({'rel_id': self.rel_id.id, 'product_id': self.product_id.id, 'cantidad': self.cantidad, 'costo': self.costo, 'proveedor': self.proveedor.id, 'condicion': self.condicion})
        return True

    @api.depends('rel_id')
    def _compute_detalle(self):
        for record in self:
            record.detalle = ''
            if record.rel_id.id:
                t = "<table class='table'><tr><td>Nombre</td><td>Descripción</td><td>Marca</td><td>Modelo</td><td>Cantidad</td><td>Presupuesto</td><td>Proveedor</td><td>Condicion</td></tr>"
                t = t+"<tr><td>"+str(record.rel_id.name)+"</td><td>"+str(record.rel_id.descripcion)+"</td><td>"+str(record.rel_id.marca)+"</td><td>"+str(record.rel_id.modelo)+"</td><td>"+str(record.rel_id.cantidad)+"</td><td>"+str(record.rel_id.presupuesto)+"</td><td>"+str(record.rel_id.proveedor)+"</td><td>"+str(record.rel_id.condicion)+"</td></tr></table>"
                record.detalle = t
