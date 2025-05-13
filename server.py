from flask import Flask, request, jsonify
import sqlite3
import requests
import datetime

app = Flask(__name__)

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS appointments
                 (id INTEGER PRIMARY KEY, date TEXT, time TEXT, name TEXT, phone TEXT, booked INTEGER)''')
    conn.commit()
    conn.close()

init_db()

# Получение слотов на дату
@app.route('/api/slots', methods=['GET'])
def get_slots():
    date = request.args.get('date')
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    
    # Пример слотов с 10:00 до 18:00 с шагом 1 час
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
    
    # Проверка, не занято ли время
    c.execute('SELECT booked FROM appointments WHERE date = ? AND time = ?', (date, time))
    result = c.fetchone()
    if result and result[0] == 1:
        conn.close()
        return jsonify({'error': 'Слот занят'}), 400

    # Сохранение записи
    c.execute('INSERT OR REPLACE INTO appointments (date, time, name, phone, booked) VALUES (?, ?, ?, ?, ?)',
              (date, time, name, phone, 1))
    conn.commit()
    conn.close()

    # Отправка SMS-уведомления
    send_sms_notification(name, phone, date, time)

    return jsonify({'status': 'success'})

# Функция отправки SMS
def send_sms_notification(name, phone, date, time):
    # В ПМР можно использовать локальные SMS-шлюзы, например, через IDC (Interdnestrcom) или сторонние API
    # Пример с использованием Twilio (замените на локальный шлюз, если Twilio недоступен)
    try:
        # Для примера: отправка на ваш номер
        admin_phone = '+37377752820'
        message = f'Новая запись: {name}, {phone}, на {date} в {time}'
        
        # Замените на реальный SMS-шлюз, доступный в ПМР
        # Например, через API Interdnestrcom или другой локальный сервис
        print(f'SMS отправлено на {admin_phone}: {message}')  # Заглушка для теста
    except Exception as e:
        print(f'Ошибка отправки SMS: {e}')

if __name__ == '__main__':
    app.run(debug=True)