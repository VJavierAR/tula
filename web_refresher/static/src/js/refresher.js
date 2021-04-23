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

            t=1;
            setInterval(function() {
                self._changeSelection(0);
            }, 1000, "JavaScript");

            self.$el.prepend($button);
            return res;
        },
    });
});
