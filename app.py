from flask import Flask, render_template, request, send_file
import sqlite3
from mock_cases import mock_cases
import csv

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    case = None
    error = None

    if request.method == 'POST':
        cnr = request.form.get('cnr').strip()
        case = mock_cases.get(cnr)
        if case:
            log_to_db(cnr, case)
        else:
            error = f"No data found for CNR {cnr}."
    return render_template('index.html', case=case, error=error)

def log_to_db(cnr, case_data):
    conn = sqlite3.connect('court_log.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cnr TEXT,
            status TEXT,
            decision_date TEXT,
            judge TEXT
        )
    ''')
    c.execute('''
        INSERT INTO logs (cnr, status, decision_date, judge)
        VALUES (?, ?, ?, ?)
    ''', (cnr, case_data['Case Status'], case_data['Decision Date'], case_data['Court and Judge']))
    conn.commit()
    conn.close()

@app.route('/export')
def export_csv():
    conn = sqlite3.connect('court_log.db')
    c = conn.cursor()
    c.execute('SELECT cnr, status, decision_date, judge FROM logs')
    rows = c.fetchall()
    conn.close()

    with open('cases.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['CNR', 'Status', 'Decision Date', 'Judge'])
        writer.writerows(rows)

    return send_file('cases.csv', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
