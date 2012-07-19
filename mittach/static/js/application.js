(function($) {
	"use strict";

	Kalendae.Input.prototype.defaults.format = "YYYY-MM-DD"; // XXX: hacky!?

	$("[data-popover-content]").each(function() {
		$(this).popover({
			title:  $(this).attr("data-popover-title") || "-",
			content: $(this).attr("data-popover-content") || "-",
			placement: "bottom"
		});
	});

	$("table").on("submit", "form", function(ev) {
        if ($(this).attr("name") == "Buchung" || $(this).attr("name") == "Loeschen"){
		var form = $(this);
		var uri = form.attr("action");
		var data = $(this).serialize();
		var id = form.closest("tr").attr("id");
		if(!id) {
			return true;
		}
		var button = $("input[type=submit]", form).prop("disabled", true);
		$.post(uri, data, function(html, status, xhr) {
			var selector = "#" + id;
            var selector2 = "div[name='alert']";
			var item = $(html).find(selector);
            var alerts = $(html).find(selector2);
			$(selector).replaceWith(item);
            $(selector2).replaceWith(alerts);
			button.prop("disabled", false); // not actually necessary due to replacement
		});
		ev.preventDefault();
        }
	});

}(jQuery));
