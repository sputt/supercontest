// Get the route without any forward slashes.
const route = window.location.pathname.replace(/\//g, '');
// Loop over the navs. If it matches the url, make it active.
$('a[id^="nav_"]').each(function () {
    let navId = $(this).attr('id').replace('nav_', '');
    if (route.includes(navId)) {
        $(this).attr('class', 'nav-link active');
    } else {
        $(this).attr('class', 'nav-link');
    }
});
