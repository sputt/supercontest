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
