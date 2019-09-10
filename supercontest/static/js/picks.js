// Some general notes:
//  * {{picks}} (array) and {{statusMap}} (dict) are passed through the template

$.each(picks, function(i, pick) {
    // Each pick is a 3 element tuple (user_id, team, points)
    const selector = pick[0] + pick[1];  // user id and picked team
    const team = pick[1];  // the raw team name
    const points = pick[2];  // points, 1.0 or 0.5 or 0.0
    if (statusMap[team] === 'P') {
        $('#' + selector).addClass('table-primary');
    } else {
        if (points === 1.0) {
            $('#' + selector).addClass('table-success');
        } else if (points === 0.5) {
            $('#' + selector).addClass('table-warning');
        } else {
            $('#' + selector).addClass('table-danger');
        }
    }
});
