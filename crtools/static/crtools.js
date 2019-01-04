var war_participations = document.querySelectorAll('[data-tooltip]');

war_participations.forEach(function(element) {
	element.addEventListener('click', function(e) {
		if( element.classList.contains('show-tooltip') ) {
			element.classList.remove('show-tooltip');
		} else {
			war_participations.forEach(function(element_remove) {
				element_remove.classList.remove('show-tooltip');
			});
			element.classList.add('show-tooltip');
		}
	});
});

var filter_dropdown = document.getElementById('member-filter');
var member_table = document.getElementById('member-table');
filter_dropdown.addEventListener('change', function(e) {
	member_table.dataset.filter = e.target.value;
})