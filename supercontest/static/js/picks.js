// Some general notes:
//  * {{all_picks}} (array) is passed through the template
//  * trim() is necessary for the team cells because jinja injects newlines
//    (this is not a problem for the headers, which are explicitly defined).

$.each(all_picks, function(i, pick) {
  const selector = pick[0] + pick[1];  // user id and picked team
  const points = pick[2]; // points, one of [1.0, 0.5, 0.0]
  if (points == 1.0) {
    $('#' + selector).addClass('table-success');
  } else if (points == 0.5) {
    $('#' + selector).addClass('table-warning');
  } else if (points == 0.0) {
    $('#' + selector).addClass('table-danger');
  } else {
    $('#' + selector).addClass('table-primary');
  };
});
