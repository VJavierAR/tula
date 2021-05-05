// Initial pager is located in source/addons/web/static/src/js/chrome/pager.js

odoo.define("refresher.pager", function(require) {
    "use strict";

    var pager = require("web.Pager");
    var AbstractController = require('web.AbstractController');
    var ListController = require('web.ListController')
    var ListRenderer = require('web.ListRenderer')
    var ListView = require('web.ListView')
    var WebClient = require('web.WebClient')
    var data_manager = require('web.data_manager');
    var inter;
    var isPaused = false;
    var idPresupuestos = 806; //id de vista lista sale.order
    var idPedidosAFacturar = 585 //Clientes.facturas
    var idTransferencias = 1794 //id vista lista stock.picking
    var idsVistasPermitidas = [idTransferencias, idPedidosAFacturar]

    // Allowed decoration on the list's rows: bold, italic and bootstrap semantics classes
    var DECORATIONS = [
        'decoration-bf',
        'decoration-it',
        'decoration-danger',
        'decoration-info',
        'decoration-muted',
        'decoration-primary',
        'decoration-success',
        'decoration-warning'
    ];

    pager.include({
        start: function() {
            var self = this;
            var res = self._super();

            var $button = $("<span>", {
                class: "fa fa-refresh btn btn-icon o_pager_refresh",
                css: {"margin-right": "8px"},
                "aria-label": "Refresh",
            });
            var $button_play = $("<span>", {
                class: "fa fa-play btn btn-icon o_pager_play",
                css: {"margin-right": "8px"},
                "aria-label": "Play",
            });
            var $button_pause = $("<span>", {
                class: "fa fa-pause btn btn-icon o_pager_pause",
                css: {"margin-right": "8px"},
                "aria-label": "Pause",
            });
            $button.on("click", function() {
                self._changeSelection(0);
            });
            $button_play.on("click", function() {
                self._playInterval();
            });
            $button_pause.on("click", function() {
                self._pauseInterval();
            });

            //console.log("self.__parentedParent: ")
            //console.log(self.__parentedParent)
            //console.log("self.__parentedParent.viewType: ")
            //console.log(self.__parentedParent.viewType)
            //undefined
            /*
            if (self.__parentedParent.viewType == "list") {
                inter = setInterval(function() {
                    self._changeSelection(0);
                }, 10000, "JavaScript");
            }
            */

            self.$el.prepend($button);
            self.$el.prepend($button_play);
            self.$el.prepend($button_pause);
            return res;
        },
        _playInterval: function() {
            //console.log("continuando....")
            isPaused = false;
        },
        _pauseInterval: function() {
            //console.log("pausando....")
            isPaused = true;
        },
    });

    AbstractController.include({
        _onOpenRecord: function (event, params) {
            event.stopPropagation();

            var record = this.model.get(event.data.id, {raw: true});
            var view_type = 'form'
            if (this.initialState.context.view_type) {
                view_type = this.initialState.context.view_type
            }
            this.trigger_up('switch_view', {
                view_type: view_type,
                res_id: record.res_id,
                mode: event.data.mode || 'readonly',
                model: this.modelName,
            });

            console.log("Di clikc en una fila")
            clearInterval(inter);

        },
    });

    ListController.include({
        _onCreateRecord: function() {
            console.log("Iniciando un formulario")
            this._super.apply(this, arguments);
            clearInterval(inter);
            for (var i = 1; i < inter; i++)
                window.clearInterval(i);
            inter = 0;
        }
    });

    ListRenderer.include({
        start: function () {
            //this._super.apply(this, arguments);
            var self = this;
            var res = self._super();


            return res;
        },
        _renderBody: function() {
            this._super.apply(this, arguments);
            var self = this;
            var $rows = this._renderRows();
            while ($rows.length < 4) {
                $rows.push(self._renderEmptyRow());
            }
            //console.log("Renderizando cuerpo de lista.....");
            //console.log(self);
            if (self.__parentedParent.viewType == "list" && idsVistasPermitidas.includes(self.__parentedParent.viewId) && !inter) {
                //console.log("*****************Mi papa es una lista y esta dentro de las vistas permitidas******************")
                inter = setInterval(function(papa) {
                    if (!isPaused) {
                        //console.log("intervalo de renderizado cada 10 seg iniciado...");
                        //console.log(papa);
                        papa.pager._changeSelection(0);
                    }
                }, 5000, self.__parentedParent);
            }
            if (self.__parentedParent.viewType == "form") {
                //console.log("*****************Mi papa es un formulario******************")
                //Deten renderizado
                clearInterval(inter);
                for (var i = 1; i < inter; i++)
                    window.clearInterval(i);
                inter = 0;
            }
            return $('<tbody>').append($rows);
        },
        /**
         * return the number of visible columns.  Note that this number depends on
         * the state of the renderer.  For example, in editable mode, it could be
         * one more that in non editable mode, because there may be a visible 'trash
         * icon'.
         *
         * @private
         * @returns {integer}
         */
        _getNumberOfCols: function () {
            var n = this.columns.length;
            return this.hasSelectors ? n + 1 : n;
        },
        /**
         * Render a complete empty row.  This is used to fill in the blanks when we
         * have less than 4 lines to display.
         *
         * @private
         * @returns {jQueryElement} a <tr> element
         */
        _renderEmptyRow: function () {
            var $td = $('<td>&nbsp;</td>').attr('colspan', this._getNumberOfCols());
            return $('<tr>').append($td);
        },

    });

    WebClient.include({
        on_menu_clicked: function (ev) {
            this._super.apply(this, arguments);
            var self = this;
            //console.log("di click en el menu")
            clearInterval(inter);
            for (var i = 1; i < inter; i++)
                window.clearInterval(i);
            inter = 0;

        },
        on_app_clicked: function (ev) {
            this._super.apply(this, arguments);
            //console.log("di click en una app")
            clearInterval(inter);
            for (var i = 1; i < inter; i++)
                window.clearInterval(i);
            inter = 0;
            var self = this;
            return this.menu_dp.add(data_manager.load_action(ev.data.action_id))
                .then(function (result) {
                    return self.action_mutex.exec(function () {
                        var completed = new Promise(function (resolve, reject) {
                            var options = _.extend({}, ev.data.options, {
                                clear_breadcrumbs: true,
                                action_menu_id: ev.data.menu_id,
                            });

                            Promise.resolve(self._openMenu(result, options))
                                   .then(function() {
                                        self._on_app_clicked_done(ev)
                                            .then(resolve)
                                            .guardedCatch(reject);
                                   }).guardedCatch(function() {
                                        resolve();
                                   });
                            setTimeout(function () {
                                    resolve();
                                }, 2000);
                        });
                        return completed;
                    });
                });
        }
    });

});
