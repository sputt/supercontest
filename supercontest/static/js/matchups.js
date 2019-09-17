// Some general notes:
//  * {{season}} (int) and {{week}} (int) and {{picks}} (array) and
//    are passed through the template.
//  * Matchup information is available in the table itself.

// Iterate through each matchup, applying home team asterisk.
$('tr.matchup').each(function() {
    const favoredTeam = $(this).find('td.favoredTeam');
    const favoredTeamName = favoredTeam.text();
    const underdogTeam = $(this).find('td.underdogTeam');
    const underdogTeamName = underdogTeam.text();
    const homeTeam = $(this).find('td.homeTeam').text();
    if (favoredTeamName === homeTeam) {
        favoredTeam.append('*')
    } else if (underdogTeamName === homeTeam) {
        underdogTeam.append('*')
    } else {
        console.warn(`The home team (${homeTeam}) is neither the ` +
                     `favored team (${favoredTeamName}) nor the ` +
                     `underdog team (${underdogTeamName}).`);
    }
});

// Iterate through each matchup, coloring the picks as necessary.
function colorPicks() {
    if (picks.length) {
        $('tr.matchup').each(function() {
            const favoredTeam = $(this).find('td.favoredTeam');
            const favoredTeamName = favoredTeam.text().replace('*', '');
            const favoredTeamScore = parseFloat($(this).find('td.favoredTeamScore').text());
            const underdogTeam = $(this).find('td.underdogTeam');
            const underdogTeamName = underdogTeam.text().replace('*', '');
            const underdogTeamScore = parseFloat($(this).find('td.underdogTeamScore').text());
            const line = parseFloat($(this).find('td.line').text());
            const gameStatus = $(this).find('td.status').text();
            const coverer = $(this).find('td.coverer').text();
            const homeTeam = $(this).find('td.homeTeam').text();
            if (gameStatus == 'P') {
                if (picks.includes(favoredTeamName)) {
                    favoredTeam.removeClass('table-info');
                    favoredTeam.addClass('table-primary');
                } else if (picks.includes(underdogTeamName)) {
                    underdogTeam.removeClass('table-info');
                    underdogTeam.addClass('table-primary');
                }
            } else {
                if (favoredTeamName === coverer) {
                    if (picks.includes(favoredTeamName)) {
                        favoredTeam.addClass('table-success');
                    } else if (picks.includes(underdogTeamName)) {
                        underdogTeam.addClass('table-danger');
                    }
                } else if (underdogTeamName === coverer) {
                    if (picks.includes(underdogTeamName)) {
                        underdogTeam.addClass('table-success');
                    } else if (picks.includes(favoredTeamName)) {
                        favoredTeam.addClass('table-danger');
                    }
                } else {
                    if (picks.includes(favoredTeamName)) {
                        favoredTeam.addClass('table-warning');
                    } else if (picks.includes(underdogTeamName)) {
                        underdogTeam.addClass('table-warning');
                    }
                }
            }
        });
    }
}
colorPicks()

// Generic CSRF token handling for the AJAX requests
// (the token is added as metadata in layout.html)
const csrftoken = $('meta[name=csrf-token]').attr('content');
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
            xhr.setRequestHeader('X-CSRFToken', csrftoken);
        }
        $('#submitButtonDiv').hide();
    },
});

// Submission of picks via AJAX.
$('#submitButton').click(function() {
    $.ajax({
        type: 'POST',
        url: '/pick',
        contentType: 'application/json; charset=UTF-8',
        data: JSON.stringify({
            'picks': picks,
            'week': week,
            'season': season,
        }),
        success: function(data) {
            $.notify('Picks submitted successfully', 'success');
            colorPicks();
        },
        error: function(request, status, message) {
            // error for serverside. the same problem is "warn" clientside.
            $.notify(request.responseText, 'error');
        },
    });
});

// Pick handling as team cells are clicked.
$('td').click(function() {
    if ($(this).hasClass('favoredTeam') || $(this).hasClass('underdogTeam')) {
        const date = new Date();
        const team = $(this).text().replace('*', '');
        const opponentColumn = $(this).hasClass('favoredTeam')
              ? 'underdogTeam' : 'favoredTeam';
        const opponent = $(this).closest('tr').find(
            'td.' + opponentColumn).text().replace('*', '');
        // Clientside validation of the pick.
        if ($(this).closest('tr').find('td.status').text() != 'P') {
            $.notify('The ' + team + ' game has already started', 'warn');
        } else if (![3, 4, 5, 6].includes(date.getDay())) {
            $.notify('Picks can only be placed Wednesday-Saturday', 'warn');
        } else if (picks.includes(opponent)) {
            $.notify('You have already selected the opposing team: ' + opponent, 'warn');
        } else if (picks.includes(team)) {
            picks.splice(picks.indexOf(team), 1);
            $(this).removeClass('table-primary');
            $(this).removeClass('table-info');
            if (picks.length) {
                $('#submitButtonDiv').show();
            } else {
                $('#submitButtonDiv').hide();
            }
        } else if (picks.length >= 5) {
            $.notify('You cannot select more than 5 teams per week', 'warn');
        } else {  // the pick is valid
            picks.push(team);
            $(this).removeClass('table-active');
            $(this).addClass('table-info');
            if (picks.length) {
                $('#submitButtonDiv').show();
            } else {
                $('#submitButtonDiv').hide();
            }
        }
    }
});

// Highlighting dark as teams are hovered over.
$('td').hover(
    function() {
        if ($(this).hasClass('favoredTeam') || $(this).hasClass('underdogTeam')) {
            $(this).css('cursor', 'pointer');
            if (!picks.includes($(this).text().replace('*', ''))) {
                $(this).addClass('table-active');
            }
        }
    },
    function() {
        if (!picks.includes($(this).text().replace('*', ''))) {
            $(this).removeClass('table-active');
        }
    }
);
