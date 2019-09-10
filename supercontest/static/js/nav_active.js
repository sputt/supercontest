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

// If by this point none of the tabs matched, you're probably in
// the main subview (eg seasons -> matchups -> weeks), so highlight
// the 'Home' nav which is meant for this.
const nonHomeToplevelEndpoints = ['rules', 'graphql', 'feedback', 'edit_user_profile'];
if (!routePaths.some(path => nonHomeToplevelEndpoints.indexOf(path) >= 0)) {
    $('#nav_home').attr('class', 'nav-link active');
}
