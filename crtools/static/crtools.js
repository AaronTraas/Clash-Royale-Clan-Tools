console.log('loaded');

var war_participations = document.querySelectorAll('td.war');

war_participations.forEach(function(element) {
	element.addEventListener('click', function(e) {
		war_participations.forEach(function(element_remove) {
			element_remove.classList.remove('show-tooltip');
		});
		element.classList.add('show-tooltip');
	});
});