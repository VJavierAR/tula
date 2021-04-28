// Initial pager is located in source/addons/web/static/src/js/chrome/pager.js

odoo.define("refresher.pager", function(require) {
    "use strict";

    var pager = require("web.Pager");
    var AbstractController = require('web.AbstractController');
    var ListController = require('web.ListController')
    var ListRenderer = require('web.ListRenderer')
    var ListView = require('web.ListView')
    var inter;
    var idPresupuestos = 806; //id de vista lista sale.order

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
            $button.on("click", function() {
                self._changeSelection(0);
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
            return res;
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
            if (self.__parentedParent.viewType == "list" && !inter) {
                console.log("*****************Mi papa es una lista******************")
                inter = setInterval(function(papa) {
                    //console.log("intervalo de renderizado cada 10 seg iniciado...");
                    //console.log(papa);
                    papa.pager._changeSelection(0);
                }, 10000, self.__parentedParent);
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

});
