// eg ['season2018', 'week4', 'matchups']
const routePath = window.location.pathname;
const routePaths = routePath.split('/')
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
if (routePath.includes('season')) {
    $('#nav_home').attr('class', 'nav-link active');
} else if (routePaths.some(path => ['sign-in', 'register'].indexOf(path) >=0)) {
    $('#nav_login').attr('class', 'nav-link active');
} else if (!routePaths.some(path => ['rules', 'graphql', 'feedback'].indexOf(path) >= 0)) {
    $('#nav_profile').attr('class', 'nav-link active');
}
