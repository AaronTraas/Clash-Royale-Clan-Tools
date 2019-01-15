Tooltip = function() {
	document.querySelectorAll('[data-tooltip]').forEach(function(element) {
	    element.addEventListener("mouseenter", function(e) {

	        var child_tooltip = e.target.querySelector('.tooltip');
	        var tooltip;
	        if(child_tooltip) {
				tooltip = child_tooltip.cloneNode(true);
	        } else {
	        	tooltip = document.createElement('div')
	        	tooltip.innerHTML = e.target.getAttribute('data-tooltip');
	        }
	        tooltip.className = "b-tooltip ";

	        document.body.appendChild(tooltip);

	        positionAt(e.target, tooltip);
	    });

	    element.addEventListener("mouseleave", function(e) {
	    	var tooltips = document.querySelector(".b-tooltip");
	    	if(tooltips) {
	    		document.body.removeChild(tooltips);
	    	}

	    });
	})

    /**
     * Positions the tooltip.
     * @param {object} parent - The trigger of the tooltip.
     * @param {object} tooltip - The tooltip itself.
     */
    function positionAt(parent, tooltip) {
	    var dist  = 2;
        var parentCoords = parent.getBoundingClientRect(), left, top;

		left = parseInt(parentCoords.left) + ((parent.offsetWidth - tooltip.offsetWidth) / 2);
		top = parseInt(parentCoords.top) - tooltip.offsetHeight - dist;

        tooltip.style.left = left + "px";
        tooltip.style.top  = top + pageYOffset + "px";
    }
};

var filter_dropdown = document.getElementById('member-filter');
var member_table = document.getElementById('member-table');
filter_dropdown.addEventListener('change', function(e) {
	member_table.dataset.filter = e.target.value;
})

var tooltip = new Tooltip();
