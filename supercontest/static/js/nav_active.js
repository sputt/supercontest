// eg ['season2018', 'week4', 'matchups']
const routePaths = window.location.pathname.split('/')
// Loop over the navs, which have been give id="nav_<route>"
// If any of them match the url subroutes, make active.
$('a[id^="nav_"]').each(function () {
    let navId = $(this).attr('id').replace('nav_', '');
    if (routePaths.includes(navId)) {
        $(this).attr('class', 'nav-link active');
    } else {
        $(this).attr('class', 'nav-link');
    }
});

// If by this point none of the tabs matched, you're either in
// the main subview (eg seasons -> matchups -> weeks), or one
// of the flask_user templates. Check and highlight that.
if (window.location.pathname.includes('season')) {
    $('#nav_home').attr('class', 'nav-link active');
} else if (!routePaths.some(path => ['rules', 'graphql', 'feedback'].indexOf(path) >= 0)) {
    $('#nav_profile').attr('class', 'nav-link active');
}
