$("td.weekScore").each(function() {
  let score = parseFloat($(this).text());
  if (score == 5.0) {
    $(this).css('color', 'forestgreen');
    $(this).css('font-weight', 'bold');
  } else if (score == 0.0) {
    $(this).css('color', 'lightcoral');
    $(this).css('font-weight', 'bold');
  };
});
