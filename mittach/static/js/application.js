(function($){
	"use strict"

	Kalendae.Input.prototype.defaults.format = "YYYYMMDD"; // XXX: hacky!?

	$("[data-popover-content]").each(function(){
		$(this).popover({
			title:  $(this).attr("data-popover-title") || "-",
			content: $(this).attr("data-popover-content") || "-",
			placement: "bottom"
		});
	});
}(jQuery))
