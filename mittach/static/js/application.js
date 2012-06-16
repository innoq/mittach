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
		var form = $(this);
		var uri = form.attr("action");
		var data = $(this).serialize();
		$.post(uri, data, function(html, status, xhr) {
			var id = "#" + form.closest("tr").attr("id");
			var item = $(html).find(id);
			$(id).replaceWith(item);
		});
		ev.preventDefault();
	});

}(jQuery));
