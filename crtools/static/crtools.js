var war_participations = document.querySelectorAll('[data-tooltip]');

war_participations.forEach(function(element) {
	element.addEventListener('click', function(e) {
		war_participations.forEach(function(element_remove) {
			element_remove.classList.remove('show-tooltip');
		});
		element.classList.add('show-tooltip');
	});
});