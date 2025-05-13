from flask import Flask, request, jsonify, render_template
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__, template_folder='../')  # шаблоны в корне проекта

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS appointments
                 (id INTEGER PRIMARY KEY, date TEXT, time TEXT, name TEXT, phone TEXT, booked INTEGER)''')
    conn.commit()
    conn.close()

init_db()

# Роут для главной страницы
@app.route('/')
def index():
    return render_template('index.html')

# Получение слотов на дату
@app.route('/api/slots', methods=['GET'])
def get_slots():
    date = request.args.get('date')
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    all_slots = ['10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00']
    c.execute('SELECT time FROM appointments WHERE date = ? AND booked = 1', (date,))
    booked_slots = [row[0] for row in c.fetchall()]
    slots = [{'time': slot, 'booked': slot in booked_slots} for slot in all_slots]
    conn.close()
    return jsonify(slots)

# Создание записи
@app.route('/api/book', methods=['POST'])
def book_appointment():
    data = request.json
    date = data['date']
    time = data['time']
    name = data['name']
    phone = data['phone']
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    c.execute('SELECT booked FROM appointments WHERE date = ? AND time = ?', (date, time))
    result = c.fetchone()
    if result and result[0] == 1:
        conn.close()
        return jsonify({'error': 'Слот занят'}), 400
    c.execute('INSERT OR REPLACE INTO appointments (date, time, name, phone, booked) VALUES (?, ?, ?, ?, ?)',
              (date, time, name, phone, 1))
    conn.commit()
    conn.close()
    send_email_to_sms(name, phone, date, time)
    return jsonify({'status': 'success'})

# Email-to-SMS
def send_email_to_sms(name, phone, date, time):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = 'ВАШ_EMAIL@gmail.com'
    sender_password = 'ВАШ_ПАРОЛЬ_ПРИЛОЖЕНИЯ'
    recipient_sms_email = '+37377752820@sms.idc.md'
    message = f'Новая запись: {name}, {phone}, на {date} в {time}'
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_sms_email
    msg['Subject'] = ''
    msg.attach(MIMEText(message, 'plain'))
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_sms_email, msg.as_string())
        server.quit()
        print(f'Email-to-SMS отправлено на {recipient_sms_email}')
    except Exception as e:
        print(f'Ошибка отправки email-to-SMS: {e}')

# Запуск сервера
if __name__ == '__main__':
    app.run(debug=True)
