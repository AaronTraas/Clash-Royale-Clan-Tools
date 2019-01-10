var tooltip_owners = document.querySelectorAll('[data-tooltip]');

tooltip_owners.forEach(function(element) {
	element.addEventListener('click', function(e) {
		if( element.classList.contains('show-tooltip') ) {
			element.classList.remove('show-tooltip');
		} else {
			tooltip_owners.forEach(function(element_remove) {
				element_remove.classList.remove('show-tooltip');
			});
			element.classList.add('show-tooltip');
		}
	});
});

function fixTooltipOrientation() {
	var table_scroll_tooltip_owners = document.querySelectorAll('.table-scroll table [data-tooltip]');
	table_scroll_tooltip_owners.forEach(function(element) {
		var tooltip = element.getElementsByClassName('tooltip')[0];
		var table = tooltip.closest('table');
		var table_y = table.offsetHeight + table.getBoundingClientRect().y + window.scrollY - 10;
		var tooltip_y = tooltip.offsetHeight + tooltip.getBoundingClientRect().y + window.scrollY;
		if( tooltip_y > table_y ) {
			tooltip.classList.add('invert');
		} else {
			tooltip.classList.remove('invert');
		}
	});
}

fixTooltipOrientation();

var filter_dropdown = document.getElementById('member-filter');
var member_table = document.getElementById('member-table');
filter_dropdown.addEventListener('change', function(e) {
	member_table.dataset.filter = e.target.value;
})