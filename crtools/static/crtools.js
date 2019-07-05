function HashParamParser() {
    function getHashParamList() {
        var hashParamPieces = unescape(window.location.hash).split('?');

        // if the hash is properly formatted, i.e., contains a single '?'
        if(hashParamPieces.length == 2) {
            var hashParams = hashParamPieces[1].split('&');

            // build dictionary of parameters
            var params = {};
            for( var index in hashParams ) {
                var parts = hashParams[index].split('=');
                var key = parts[0];
                var value = parts.length == 2 ? parts[1] : null;
                params[key] = value;
            }

            // return dict of params
            return params;
        } else {
            // no params found; return empty dict
            return {};
        }
    }

    function getHashParam(key) {
        var params = getHashParamList();
        if( key in params ) {
            return params[key];
        } else {
            return null;
        }
    }

    function setHashParam(key, newvalue) {
        var params = getHashParamList();

        if( (newvalue == null) && (key in params) ) {
            delete params[key];
        } else {
            // update value of param
            params[key] = newvalue;
        }

        // build list of params and write to window.location.hash
        if( Object.keys(params).length == 0 ) {
            if("pushState" in history) {
                history.pushState("", document.title, window.location.pathname + window.location.search);
            } else {
                window.location.hash = '?';
            }
        } else {
            var paramStrings = [];
            for( var param_key in params ) {
                var value = params[param_key]
                if(value) {
                    paramStrings.push(param_key + '=' + value);
                } else {
                    paramStrings.push(param_key);
                }
            }
            window.location.hash = '?' + paramStrings.join('&');
        }
    }

    return {
        'set' : function(key, newvalue) {
            setHashParam(key, newvalue);
        },
        'get' : function(key) {
            return getHashParam(key);
        }
    };
}

function TooltipManager() {
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
        tooltip.addEventListener('click', function(e) {
            clearTooltip(this, true);
        });

        document.body.appendChild(tooltip);

        positionAt(element, tooltip);
    }

    function clearTooltips(force) {
        var tooltips = document.querySelectorAll('.b-tooltip');

        if(tooltips) {
            tooltips.forEach( function(tooltip) {
                clearTooltip(tooltip, force)
            });
        }
    }

    function clearTooltip(tooltip, force) {
        var persist = (tooltip.dataset.persist=='true')
        if( !persist || force ) {
            document.body.removeChild(tooltip);
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
}

function MemberTableFilter() {
    var filter_dropdown = document.getElementById('member-filter');
    var member_table = document.getElementById('member-table');

    var hashParams = HashParamParser();

    filter_dropdown.addEventListener('change', function(e) {
        setFilter(e.target.value);
        if(e.target.value=='none') {
            hashParams.set('filter', null);
        } else {
            hashParams.set('filter', e.target.value);
        }
    });

    getFilterFromHash();

    function setFilter(filter) {
        member_table.dataset.filter = filter;
    }

    function getFilterFromHash() {
        var filter = hashParams.get('filter');
        if(filter) {
            setFilter(filter);
            filter_dropdown.value = filter;
        }
    }
}

function LeaderboardFilter() {
    var leaderboard_container = document.getElementById('leaderboards');

    document.getElementById('leaderboard-filter').addEventListener('change', function(e) {
        leaderboard_container.dataset.filter = e.target.value;
    });
}

function DialogHandler() {

    var detailDivs = document.querySelectorAll('dialog [data-member-id]')

    function showMemberInfo(memberTag) {
        detailDivs.forEach(function(element) {
            if(element.dataset.memberId == memberTag) {
                element.className = 'show'
            } else {
                element.className = ''
            }
        });
    }

    document.querySelectorAll('.dialog-shadow, dialog [data-role="close"]').forEach(function(element) {
        element.addEventListener('click', function(e) {
            e.preventDefault();
            document.body.dataset.activeDialog = 'none';
        });
    });

    document.querySelectorAll('[data-role="dialog-show"]').forEach(function(element) {
        var target = element.dataset.target;
        element.addEventListener('click', function(e) {
            e.preventDefault();
            document.body.dataset.activeDialog = target;

            if (target == 'member-detail') {
                showMemberInfo(element.dataset.memberTag)
            }

            return true;
        });
    });
}
