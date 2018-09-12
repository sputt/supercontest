from flask import render_template
from supercontest import APP


@APP.route('/')
def home():
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

    return render_template('home.html', week=week, trs=trs_str)
