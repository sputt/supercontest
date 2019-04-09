// Some general notes:
//  * {{week}} (int) and {{picks}} (array) and {{matchups}} (dict) are defined
//    in templates.
//  * trim() is necessary for the team cells because jinja injects newlines
//    (this is not a problem for the headers, which are explicitly defined).

// Iterate through existing picks (if any) and highlight those cells.
if (picks.length) {
  $("tr.matchup").each(function() {
    let favoredTeam = $(this).find("td.favoredTeam");
    let favoredTeamName = favoredTeam.text().trim().replace("*", "");
    let favoredTeamScore = parseFloat($(this).find("td.favoredTeamScore").text());
    let underdogTeam = $(this).find("td.underdogTeam");
    let underdogTeamName = underdogTeam.text().trim().replace("*", "");
    let underdogTeamScore = parseFloat($(this).find("td.underdogTeamScore").text());
    let line = parseFloat($(this).find("td.line").text());
    let status = $(this).find("td.status").text();
    if (status == 'P') {
      if (picks.includes(favoredTeamName)) {
        favoredTeam.addClass('highlighted');
      };
      if (picks.includes(underdogTeamName)) {
        underdogTeam.addClass('highlighted');
      };
    } else {
      // TODO: this logic is done in python serverside, and is returned through the matchups.winner var. Deduplicate here.
      if ((favoredTeamScore - underdogTeamScore) > line) {
        if (picks.includes(favoredTeamName)) {
          favoredTeam.css('background-color', 'palegreen');
        };
        if (picks.includes(underdogTeamName)) {
          underdogTeam.css('background-color', 'lightcoral');
        };
      } else if ((favoredTeamScore - underdogTeamScore) == line) {
        if (picks.includes(favoredTeamName)) {
          favoredTeam.css('background-color', 'khaki');
        };
        if (picks.includes(underdogTeamName)) {
          underdogTeam.css('background-color', 'khaki');
        };
      } else {
        if (picks.includes(favoredTeamName)) {
          favoredTeam.css('background-color', 'lightcoral');
        };
        if (picks.includes(underdogTeamName)) {
          underdogTeam.css('background-color', 'palegreen');
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
      xhr.setRequestHeader("X-CSRFToken", csrftoken)
    };
    $('#submitButtonDiv').hide();
  }
})

// Submission of picks via AJAX
$('#submitButton').click(function() {
  $.ajax({
    type: "POST",
    url: "/pick",
    contentType: 'application/json; charset=UTF-8',
    data: JSON.stringify({
      "picks": picks,
      "week": week
    }),
    success: function(data) {
      $.notify("Picks submitted successfully", "success");
    },
    error: function(request, status, message) {
      $.notify(request.responseText, "error");  // error for serverside. the same problem is "warn" clientside.
    }
  })
});

// Pick handling as team cells are clicked
$('td').click(function () {
  if ($(this).hasClass('favoredTeam') || $(this).hasClass('underdogTeam')) {
    let date = new Date()
    let team = $(this).text().trim().replace("*", "");
    let opponentColumn = ($(this).hasClass('favoredTeam')) ? 'underdogTeam' : 'favoredTeam';
    let opponent = $(this).closest('tr').find('td.' + opponentColumn).text().trim().replace("*", "");
    if ($(this).closest('tr').find('td.status').text() != "P") {
      $.notify("The " + team + " game has already started", "warn");
    } else if (![1,2,3,4,5,6,7].includes(date.getDay())) {
      $.notify("Picks can only be placed Wednesday-Saturday", "warn");
    } else if (picks.includes(opponent)) {
      $.notify("You have already selected the opposing team: " + opponent, "warn");
    } else if (picks.includes(team)) {
      picks.splice(picks.indexOf(team), 1);
      $(this).removeClass('highlighted')
      if (picks.length) {
        $('#submitButtonDiv').show();
      } else {
        $('#submitButtonDiv').hide();
      };
    } else if (picks.length >= 5) {
      $.notify("You cannot select more than 5 teams per week", "warn");
    } else {
      picks.push(team)
      $(this).addClass('highlighted');
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
  function () {
    if ($(this).hasClass('favoredTeam') || $(this).hasClass('underdogTeam')) {
      $(this).css('cursor', 'pointer');
      if (!picks.includes($(this).text().trim().replace("*", ""))) {
        $(this).addClass('highlighted');
      };
    };
  },
  function () {
    if (!picks.includes($(this).text().trim().replace("*", ""))) {
      $(this).removeClass('highlighted');
    }
});
