
odoo.define('invoice.action_button', function (require) {
"use strict";

    var core = require('web.core');
    var ListController = require('web.ListController');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var _t = core._t;

    ListController.include({
        renderButtons: function($node) {
        this._super.apply(this, arguments);
            if (this.$buttons) {
                if (typeof this.actionViews !== 'undefined' && this.actionViews.length > 0) {
                    switch (this.actionViews[0].viewID) {
                      case 2940:
                        this.$buttons.find('.o_button_import').hide();
                        this.$buttons.find('.o_list_button_add').hide();
                        this.$buttons.find('.oe_action_button_ticket_report').click(this.proxy('action_inter5'));
                        this.$buttons.find('.oe_action_button_helpdesk_detalle').click(this.proxy('action_inter11'));
                        this.$buttons.find('.oe_action_button_helpdesk_guia').click(this.proxy('action_inter13'));
                        break;
                      case 2941:
                        this.$buttons.find('.o_button_import').hide();
                        this.$buttons.find('.o_list_button_add').hide();
                        this.$buttons.find('.oe_action_button').click(this.proxy('action_inter2'));
                        break; 
                      case 646:
                        this.$buttons.find('.o_button_import').hide();
                        this.$buttons.find('.oe_action_button_stock_inventory').click(this.proxy('action_inter6'));
                        break;
                      case 3122:
                        this.$buttons.find('.o_button_import').hide();
                        this.$buttons.find('.oe_action_button_stock_rule').click(this.proxy('action_inter10'));
                        break;
                      case 672:
                        this.$buttons.find('.o_button_import').hide();
                        this.$buttons.find('.o_list_button_add').hide();
                        this.$buttons.find('.oe_action_button_stock_rule').click(this.proxy('action_inter10')).hide();
                        break;
                      case 3605:
                        this.$buttons.find('.oe_action_button_picking_unassigned').click(this.proxy('action_inter16'));
                      default:
                        this.$buttons.find('.oe_action_button_res_partner').click(this.proxy('action_inter15'));
                        this.$buttons.find('.oe_action_button_lot_serial').click(this.proxy('action_inter14')); 
                        this.$buttons.find('.oe_action_button_helpdesk_detalle').hide();
                        this.$buttons.find('.oe_action_button_purchase_order').click(this.proxy('action_inter8')); 
                        this.$buttons.find('.oe_action_button_sale_report').click(this.proxy('action_inter4')); 
                        this.$buttons.find('.oe_action_button_ticket_report').hide();
                        this.$buttons.find('.o_button_import').hide();
                        this.$buttons.find('.oe_action_button').hide();
                        this.$buttons.find('.oe_action_button_move_line').click(this.proxy('action_inter1'));
                        this.$buttons.find('.oe_action_button_product_product').click(this.proxy('action_inter7'));
                        this.$buttons.find('.oe_action_button_product_product_one').click(this.proxy('action_inter9'));
                        this.$buttons.find('.oe_action_button_stock_quant').click(this.proxy('action_inter3'));
                        this.$buttons.find('.oe_action_button_creacion_ruta').click(this.proxy('action_inter12')); 
                        
                    }
                }
                
            }
        },
        action_inter16: function (e) {
            var self = this
            var user = session.uid;
            self.do_action({
                name: _t('Desasignar'),
                type : 'ir.actions.act_window',
                res_model: 'picking.desasignar',
                view_type: 'form',
                view_mode: 'form',
                view_id: 'view_picking_desasignar',
                views: [[false, 'form']],
                target: 'new',
            
            });
        }
        ,
            action_inter15: function (e) {
            var self = this
            var user = session.uid;
            self.do_action({
                name: _t('Reporte de clientes'),
                type : 'ir.actions.act_window',
                res_model: 'clientes.reporte',
                view_type: 'form',
                view_mode: 'form',
                view_id: 'view_clientes_reporte',
                views: [[false, 'form']],
                target: 'new',
            
            });
        }
        ,
        action_inter14: function (e) {
            var self = this
            var user = session.uid;
            self.do_action({
                name: _t('Base Instalada'),
                type : 'ir.actions.act_window',
                res_model: 'lot.serial.reporte',
                view_type: 'form',
                view_mode: 'form',
                view_id: 'view_lot_serial_reporte',
                views: [[false, 'form']],
                target: 'new',
            
            });
        }
        ,
        action_inter13: function (e) {
            var self = this
            var user = session.uid;
            self.do_action({
                name: _t('Guias a ticket'),
                type : 'ir.actions.act_window',
                res_model: 'ticket.guia.carga',
                view_type: 'form',
                view_mode: 'form',
                view_id: 'view_helpdesk_guia_form',
                views: [[false, 'form']],
                target: 'new',
            
            });
        }
        ,
        action_inter12: function (e) {
            var self = this
            var user = session.uid;
            self.do_action({
                name: _t('Reporte de expedición'),
                type : 'ir.actions.act_window',
                res_model: 'reporte.creacion.ruta',
                view_type: 'form',
                view_mode: 'form',
                view_id: 'view_reporte_creacion_ruta_action_form',
                views: [[false, 'form']],
                target: 'new',
            
            });
        },
        action_inter11: function (e) {
            var self = this
            var user = session.uid;
            self.do_action({
                name: _t('Detalle Ticket'),
                type : 'ir.actions.act_window',
                res_model: 'helpdesk.detalle.ticket',
                view_type: 'form',
                view_mode: 'form',
                view_id: 'view_helpdesk_detalle_ticket_action_form',
                views: [[false, 'form']],
                target: 'new',
            
            });
        },
        action_inter10: function (e) {
            var self = this
            var user = session.uid;
            self.do_action({
                name: _t('Importacion'),
                type : 'ir.actions.act_window',
                res_model: 'stock.warehouse.orderpoint.import',
                view_type: 'form',
                view_mode: 'form',
                view_id: 'view_stock_warehousw_orderpoint_import_action_form',
                views: [[false, 'form']],
                target: 'new',
            
            });
        },
        action_inter9: function (e) {
            var self = this
            var user = session.uid;
            self.do_action({
                name: _t('Alta'),
                type : 'ir.actions.act_window',
                res_model: 'product.product.one',
                view_type: 'form',
                view_mode: 'form',
                view_id: 'view_product_product_one_action_form',
                views: [[false, 'form']],
                target: 'new',
            
            });
        },
        action_inter8: function (e) {
            var self = this
            var user = session.uid;
            self.do_action({
                name: _t('Reporte'),
                type : 'ir.actions.act_window',
                res_model: 'purchase.order.action',
                view_type: 'form',
                view_mode: 'form',
                view_id: 'view_purchase_order_action_form',
                views: [[false, 'form']],
                target: 'new',
            
            });
        },
        action_inter7: function (e) {
            var self = this
            var user = session.uid;
            self.do_action({
                name: _t('Inventario'),
                type : 'ir.actions.act_window',
                res_model: 'product.product.action',
                view_type: 'form',
                view_mode: 'form',
                view_id: 'view_product_product_action_form',
                views: [[false, 'form']],
                target: 'new',
            
            });
        },
        action_inter6: function (e) {
            var self = this
            var user = session.uid;
            self.do_action({
                name: _t('Inventario'),
                type : 'ir.actions.act_window',
                res_model: 'stock.inventory.action',
                view_type: 'form',
                view_mode: 'form',
                view_id: 'view_stock_inventory_action_form',
                views: [[false, 'form']],
                target: 'new',
            
            });
        },
         action_inter5: function (e) {
            var self = this
            var user = session.uid;
            self.do_action({
                name: _t('Tickets'),
                type : 'ir.actions.act_window',
                res_model: 'helpdesk.ticket.action',
                view_type: 'form',
                view_mode: 'form',
                view_id: 'view_helpdesk_ticket_action_form',
                views: [[false, 'form']],
                target: 'new',
            
            });
        },
        action_inter4: function (e) {
            var self = this
            var user = session.uid;
            self.do_action({
                name: _t('Solicitudes'),
                type : 'ir.actions.act_window',
                res_model: 'sale.order.action',
                view_type: 'form',
                view_mode: 'form',
                view_id: 'view_sale_order_action_form',
                views: [[false, 'form']],
                target: 'new',
            
            });
        },
        action_inter3: function (e) {
            var self = this
            var user = session.uid;
            self.do_action({
                name: _t('Existencias'),
                type : 'ir.actions.act_window',
                res_model: 'stock.quant.action',
                view_type: 'form',
                view_mode: 'form',
                view_id: 'view_stock_quant_action_form',
                views: [[false, 'form']],
                target: 'new',
            
            });
        },


        action_inter2: function (e) {
            var self = this
            var user = session.uid;
            self.do_action({
                name: _t('Transferencias Internas'),
                type : 'ir.actions.act_window',
                res_model: 'transferencia.interna',
                view_type: 'form',
                view_mode: 'form',
                view_id: 'view_transferencia_interna',
                views: [[false, 'form']],
                target: 'new',
            }, {
                on_reverse_breadcrumb: function () {
                    self.update_control_panel({clear: true, hidden: true});
                }
            });


            rpc.query({
                model: 'stock.picking',
                method: 'inter_wizard',
                args: [[user],{'id':user}],
            });
        },
        action_inter1: function (e) {
            var self = this
            var user = session.uid;
            self.do_action({
                name: _t('Movimientos'),
                type : 'ir.actions.act_window',
                res_model: 'stock.move.action',
                view_type: 'form',
                view_mode: 'form',
                view_id: 'view_stock_move_action_form',
                views: [[false, 'form']],
                target: 'new',
            
            });
        },
        receive_invoice: function () {
            var self = this
            var user = session.uid;
            rpc.query({
                model: 'stock.picking',
                method: 'inter_wizard',
                args: [[user],{'id':user}],
                }).then(function (e) {
                    self.do_action({
                        name: _t('action_invoices'),
                        type: 'ir.actions.act_window',
                        res_model: 'name.name',
                        views: [[false, 'form']],
                        view_mode: 'form',
                        target: 'new',
                    });
                    window.location
                });
        },
    });
});