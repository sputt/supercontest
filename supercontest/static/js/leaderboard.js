// data is passed through jinja

const layout = {
  title: 'Season Totals',
  xaxis: {
    title: 'Week',
    tickvals: [...Array(17+1).keys()],
  },
  yaxis: {
    title: 'Cumulative Points',
  },
};

Plotly.plot('scoreGraph', data, layout);

$('td.weekScore').each(function() {
  const score = parseFloat($(this).text());
  if (score == 5.0) {
    $(this).css('color', 'forestgreen');
    $(this).css('font-weight', 'bold');
  } else if (score == 0.0) {
    $(this).css('color', 'lightcoral');
    $(this).css('font-weight', 'bold');
  };
});
