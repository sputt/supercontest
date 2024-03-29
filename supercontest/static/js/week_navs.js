// Get the route (eg week14) without any other portions: domain, forward
// slashes, subdomains, etc.
const route = window.location.pathname.match(/\/week(.*)\//g)[0].replace(/\//g, '');
// Loop over the weeknav_week## navs. If it matches the url, make it
// active. If that week isn't in the db, disable the menu link.
$('a[id^="weeknav_"]').each(function () {
    let weekStr = $(this).attr('id').replace('weeknav_', '');
    let weekNum = parseInt(weekStr.replace('week', ''));
    if (weekStr === route) {
        $(this).attr('class', 'nav-link active');
    } else if (available_weeks.includes(weekNum)) {
        $(this).attr('class', 'nav-link');
    } else {
        $(this).attr('class', 'nav-link disabled');
    }
});
