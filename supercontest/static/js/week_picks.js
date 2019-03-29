// Some general notes:
//  * {{all_picks}} (array) is passed through the template
//  * trim() is necessary for the team cells because jinja injects newlines
//    (this is not a problem for the headers, which are explicitly defined).

$.each(all_picks, function(i, pick) {
  let selector = pick[0].replace(/\@/g, "").replace(/\./g, "") + pick[1];  // email+team, no @ or .
  let points = pick[2];  // 1.0, 0.5, 0.0
  if (points == 1.0) {
    $("#" + selector).css('background-color', 'palegreen');
  } else if (points == 0.5) {
    $("#" + selector).css('background-color', 'khaki');
  } else if (points == 0.0) {
    $("#" + selector).css('background-color', 'lightcoral');
  } else {
    $("#" + selector).addClass('highlighted');
  };
});
