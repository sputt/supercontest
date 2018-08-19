from flask import Flask, render_template


APP = Flask(__name__)


@APP.route('/')
def render_lines_with_scores():
    """Formats our results (list of lists) into an HTML table.
    """
    week, results = compare_scores_to_lines()
    trs_list = []
    for result in results:
        status = result.pop(-1)
        tds_list = ['<td>{}</td>'.format(cell) for cell in result]
        if status == 'game is over':
            if float(result[-1]) > float(result[-2]):
                tds_list[0] = tds_list[0].replace('td', 'td bgcolor=lightgreen', 1)
            elif float(result[-2]) == float(result[-1]):
                tds_list[0] = tds_list[0].replace('td', 'td bgcolor=lightblue', 1)
                tds_list[1] = tds_list[1].replace('td', 'td bgcolor=lightblue', 1)
            else:
                tds_list[1] = tds_list[1].replace('td', 'td bgcolor=lightgreen', 1)
        tds_str = ''.join(tds_list)
        trs_list.append('<tr>{}</tr>'.format(tds_str))
    trs_str = ''.join(trs_list)

    return render_template('results.html', week=week, trs=trs_str)


if __name__ == '__main__':
    APP.run(host='0.0.0.0', debug=True)
