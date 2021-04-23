// Initial pager is located in source/addons/web/static/src/js/chrome/pager.js

odoo.define("refresher.pager", function(require) {
    "use strict";

    var pager = require("web.Pager");
    var AbstractController = require('web.AbstractController');
    var inter;

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

            console.log("self.__parentedParent: ")
            console.log(self.__parentedParent)
            console.log("self.__parentedParent.viewType: ")
            console.log(self.__parentedParent.viewType)
            //undefined

            if (self.__parentedParent.viewType == "list") {
                inter = setInterval(function() {
                    self._changeSelection(0);
                }, 10000, "JavaScript");
            }

            /*
            $(this).parents("tr").find(".o_data_row").on("click", function() {
                console.log("Di clikc en una fila")
                clearInterval(inter);
            });
            */
            self.$el.prepend($button);
            return res;
        },
    });

    AbstractController.include({
        _onOpenRecord: function (event, params) {
            event.stopPropagation();
            /*
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
            */
            console.log("Di clikc en una fila")
            clearInterval(inter);

        },
    });
});
