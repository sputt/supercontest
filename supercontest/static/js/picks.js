$.each(sorted_picks, function(i, pick_set) {
    // Each pick_set is a 2 element tuple (user_id, [teams])
    const user_id = pick_set[0];
    const teams = pick_set[1];
    teams.forEach(function (team, index) {
        const selector = user_id.toString() + team;
        const points = pointsMap[team];
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
});
