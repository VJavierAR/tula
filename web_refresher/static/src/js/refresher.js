// Initial pager is located in source/addons/web/static/src/js/chrome/pager.js

odoo.define("refresher.pager", function(require) {
    "use strict";

    var pager = require("web.Pager");
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
            console.log(self.__parentedParent.)
            console.log("self.__parentedParent.viewType: ")
            console.log(self.__parentedParent.viewType)
            setInterval(function() {
                self._changeSelection(0);
            }, 10000, "JavaScript");

            self.$el.prepend($button);
            return res;
        },
    });
});
