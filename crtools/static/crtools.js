Tooltip = function() {
    document.querySelectorAll('[data-tooltip]').forEach(function(element) {
        element.addEventListener('mouseenter', function(e) {
            addTooltip(element, false);
        });

        element.addEventListener('click', function(e) {
        	clearTooltips(true);
            addTooltip(element, true);
        });

        element.addEventListener('mouseleave', function(e) {
        	clearTooltips(false);
        });
    })

    function addTooltip(element, persist) {
        var child_tooltip = element.querySelector('.tooltip');
        var tooltip;
        if(child_tooltip) {
            tooltip = child_tooltip.cloneNode(true);
        } else {
            tooltip = document.createElement('div')
            tooltip.innerHTML = element.getAttribute('data-tooltip');
        }
        tooltip.className = 'b-tooltip';
        tooltip.dataset.persist = persist;

        document.body.appendChild(tooltip);

        positionAt(element, tooltip);
    }

    function clearTooltips(force) {
        var tooltips = document.querySelectorAll('.b-tooltip');

        if(tooltips) {
        	tooltips.forEach( function(tooltip) {
        		persist = (tooltip.dataset.persist=='true')
        		console.log('persist, force', persist, force)
        		if( !persist || force ) {
		            document.body.removeChild(tooltip);
        		}
        	})
        }
    }

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

        tooltip.style.left = left + 'px';
        tooltip.style.top  = top + pageYOffset + 'px';
    }
};

var filter_dropdown = document.getElementById('member-filter');
var member_table = document.getElementById('member-table');
filter_dropdown.addEventListener('change', function(e) {
    member_table.dataset.filter = e.target.value;
})

var tooltip = new Tooltip();
