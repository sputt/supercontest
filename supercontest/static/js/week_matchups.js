// Some general notes:
//  * {{week}} (int) and {{picks}} (array) and {{matchups}} (dict) are defined
//    in templates.
//  * trim() is necessary for the team cells because jinja injects newlines
//    (this is not a problem for the headers, which are explicitly defined).

// Iterate through existing picks (if any) and highlight those cells.
if (picks.length) {
  $('tr.matchup').each(function() {
    const favoredTeam = $(this).find('td.favoredTeam');
    const favoredTeamName = favoredTeam.text().trim().replace('*', '');
    const favoredTeamScore = parseFloat($(this).find(
        'td.favoredTeamScore').text());
    const underdogTeam = $(this).find('td.underdogTeam');
    const underdogTeamName = underdogTeam.text().trim().replace('*', '');
    const underdogTeamScore = parseFloat($(this).find(
        'td.underdogTeamScore').text());
    const line = parseFloat($(this).find('td.line').text());
    const status = $(this).find('td.status').text();
    if (status == 'P') {
      if (picks.includes(favoredTeamName)) {
        favoredTeam.addClass('table-primary');
      };
      if (picks.includes(underdogTeamName)) {
        underdogTeam.addClass('table-primary');
      };
    } else {
      // This logic is done in python serverside, and is returned
      // through the matchups.winner var. You could deduplicate it here,
      // but then you'd have to call calculate_leaderboard() every time
      // the main page (matchups) is refreshed. This is totally doable,
      // but is not ideal during live scorewatching.
      if ((favoredTeamScore - underdogTeamScore) > line) {
        if (picks.includes(favoredTeamName)) {
          favoredTeam.addClass('table-success');
        };
        if (picks.includes(underdogTeamName)) {
          underdogTeam.addClass('table-danger');
        };
      } else if ((favoredTeamScore - underdogTeamScore) == line) {
        if (picks.includes(favoredTeamName)) {
          favoredTeam.addClass('table-warning');
        };
        if (picks.includes(underdogTeamName)) {
          underdogTeam.addClass('table-warning');
        };
      } else {
        if (picks.includes(favoredTeamName)) {
          favoredTeam.addClass('table-danger');
        };
        if (picks.includes(underdogTeamName)) {
          underdogTeam.addClass('table-success');
        };
      };
    };
  });
};

// Generic CSRF token handling for the AJAX requests
// (the token is added as metadata in layout.html)
const csrftoken = $('meta[name=csrf-token]').attr('content');
$.ajaxSetup({
  beforeSend: function(xhr, settings) {
    if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
      xhr.setRequestHeader('X-CSRFToken', csrftoken);
    };
    $('#submitButtonDiv').hide();
  },
});

// Submission of picks via AJAX
$('#submitButton').click(function() {
  $.ajax({
    type: 'POST',
    url: '/pick',
    contentType: 'application/json; charset=UTF-8',
    data: JSON.stringify({
      'picks': picks,
      'week': week,
    }),
    success: function(data) {
      $.notify('Picks submitted successfully', 'success');
    },
    error: function(request, status, message) {
      // error for serverside. the same problem is "warn" clientside.
      $.notify(request.responseText, 'error');
    },
  });
});

// Pick handling as team cells are clicked
$('td').click(function() {
  if ($(this).hasClass('favoredTeam') || $(this).hasClass('underdogTeam')) {
    const date = new Date();
    const team = $(this).text().trim().replace('*', '');
    const opponentColumn = $(this).hasClass('favoredTeam')
          ? 'underdogTeam' : 'favoredTeam';
    const opponent = $(this).closest('tr').find(
        'td.' + opponentColumn).text().trim().replace('*', '');
    if ($(this).closest('tr').find('td.status').text() != 'P') {
      $.notify('The ' + team + ' game has already started', 'warn');
    } else if (![3, 4, 5, 6].includes(date.getDay())) {
      $.notify('Picks can only be placed Wednesday-Saturday', 'warn');
    } else if (picks.includes(opponent)) {
      $.notify('You have already selected the opposing team: ' + opponent,
          'warn');
    } else if (picks.includes(team)) {
      picks.splice(picks.indexOf(team), 1);
      $(this).removeClass('table-primary');
      if (picks.length) {
        $('#submitButtonDiv').show();
      } else {
        $('#submitButtonDiv').hide();
      };
    } else if (picks.length >= 5) {
      $.notify('You cannot select more than 5 teams per week', 'warn');
    } else {  // the pick is valid
      picks.push(team);
      $(this).removeClass('table-active');
      $(this).addClass('table-primary');
      if (picks.length) {
        $('#submitButtonDiv').show();
      } else {
        $('#submitButtonDiv').hide();
      };
    };
  };
});

// Highlighting as teams are hovered over
$('td').hover(
    function() {
      if ($(this).hasClass('favoredTeam') || $(this).hasClass('underdogTeam')) {
        $(this).css('cursor', 'pointer');
        if (!picks.includes($(this).text().trim().replace('*', ''))) {
          $(this).addClass('table-active');
        };
      };
    },
    function() {
      if (!picks.includes($(this).text().trim().replace('*', ''))) {
        $(this).removeClass('table-active');
      }
    }
);
