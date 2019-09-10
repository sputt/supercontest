$('td.weekScore').each(function() {
    const score = parseFloat($(this).text());
    const week = $(this).closest('table').find('th').eq($(this).index()).text();
    if (week <= colorWeek) {
        if (score == 5.0) {
            $(this).css('color', 'forestgreen');
            $(this).css('font-weight', 'bold');
        } else if (score == 0.0) {
            $(this).css('color', 'lightcoral');
            $(this).css('font-weight', 'bold');
        }
    }
});
