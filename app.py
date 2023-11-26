
import logging
import os
import datetime
# Import Flask và Flask-Mail
# from flask import Flask

# from flask_mail import Mail, Message

# from flask import render_template

from datetime import datetime, timedelta

from logging.handlers import TimedRotatingFileHandler

from flask import Flask, render_template, request, redirect, url_for, flash,session

from connect import create_connection  # Import hàm tạo kết nối

from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import UniqueConstraint

from datetime import datetime, timezone
# Tạo thư mục logs nếu nó không tồn tại
if not os.path.exists('logs'):
    os.makedirs('logs')

# Cấu hình logging
logging.basicConfig(filename='logs/app.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

# db = SQLAlchemy()

app = Flask(__name__)

# class Task(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(255), nullable=False)
    
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://username:password@localhost/db_name?driver=ODBC+Driver+17+for+SQL+Server'


# db.init_app(app)
# # Cấu hình Flask-Mail
# app.config['MAIL_SERVER'] = 'smtp.example.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = False
# app.config['MAIL_USERNAME'] = 'your_username'
# app.config['MAIL_PASSWORD'] = 'your_password'
# app.config['MAIL_DEFAULT_SENDER'] = 'your_email@example.com'
# # Khởi tạo đối tượng Mail
# mail = Mail(app)

app.secret_key = 'admin' # Điều này là mật khẩu bảo mật session,

# Sử dụng hàm create_connection từ connect.py để tạo kết nối
conn = create_connection()

# Tạo đối tượng cursor để thực hiện các truy vấn SQL
cursor = conn.cursor()

# Tạo bảng tasks nếu chưa tồn tại
cursor.execute('''
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'tasks')
    CREATE TABLE tasks (
        id INT PRIMARY KEY IDENTITY(1,1),
        name NVARCHAR(255) NOT NULL,
        description NVARCHAR(MAX),
        status NVARCHAR(50) NOT NULL
    )
''')
conn.commit()

current_time_naive = datetime.now()  # Thời gian naive, không có thông tin về múi giờ

# Định nghĩa biến last_login_time
last_login_time = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

# Sử dụng biến last_login_time trong một hàm
def calculate_time_difference():
    current_time_naive = datetime.now()
    current_time_aware = current_time_naive.replace(tzinfo=timezone.utc)

    time_difference = current_time_aware - last_login_time
    return time_difference

# Gọi hàm để sử dụng biến last_login_time
result = calculate_time_difference()

last_login_time_aware = last_login_time  # Thời gian aware, có thông tin về múi giờ

current_time_aware = current_time_naive.replace(tzinfo=timezone.utc)

time_difference = current_time_aware - last_login_time_aware

# Hàm để lấy danh sách công việc
def get_tasks():
    cursor.execute('SELECT * FROM tasks')
    return cursor.fetchall()


# Hàm để thêm công việc mới
def add_task(name, description, status='Pending'):
    try:
        cursor.execute('''
            INSERT INTO tasks (name, description, status)
            VALUES (?, ?, ?)
        ''', (name, description, status))
        conn.commit()
        logging.info(f"Task added: {name}")
    except Exception as e:
        flash(f"Error adding task: {str(e)}", 'error')
        logging.error(f"Error adding task: {str(e)}")


# Hàm để cập nhật trạng thái công việc
def update_task_status(task_id, new_status):
    try:
        cursor.execute('''
            UPDATE tasks
            SET status = ?
            WHERE id = ?
        ''', (new_status, task_id))
        conn.commit()
        logging.info(f"Task status updated: Task ID {task_id}, New Status: {new_status}")
    except Exception as e:
        flash(f"Error updating task status: {str(e)}", 'error')
        logging.error(f"Error updating task status: {str(e)}")


# Hàm để xóa công việc
def delete_task(task_id):
    try:
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        logging.info(f"Task deleted: Task ID {task_id}")
    except Exception as e:
        flash(f"Error deleting task: {str(e)}", 'error')
        logging.error(f"Error deleting task: {str(e)}")

# Mock function for user authentication
def authenticate_user(username, password):
    # Replace this with your actual authentication logic
    if username == 'guest' and password == 'password':
        return True
    else:
        return False
    
#Route mặc định khi start
@app.route('/')
def home():
    if 'username' in session and 'last_login_time' in session:
        current_time = datetime.now(timezone.utc)
        last_login_time = session['last_login_time']
        time_difference = (current_time - last_login_time).seconds

        if time_difference < 300:  # 300 seconds = 5 minutes
            #return f'Chào mừng {session["username"]}, bạn đã đăng nhập thành công!'
            return render_template('index.html', username=session['username'])
        else:
            # Nếu hết thời gian session, xóa session và hiển thị lại form đăng nhập
            session.pop('username', None)
            session.pop('last_login_time', None)

    return redirect(url_for('login'))
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Thực hiện truy vấn SQL để kiểm tra thông tin đăng nhập
        query = f"SELECT * FROM Users WHERE Username = '{username}' AND Password = '{password}'"
        result = cursor.execute(query).fetchone()

        if result:
            # Lưu thông tin đăng nhập vào session
            session['username'] = username
            session['last_login_time'] = datetime.now()

            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Đăng nhập thất bại. Vui lòng thử lại.')

    return render_template('login.html', error='')
# @app.route('/index')
# def success():
#     tasks = get_tasks()
#     return render_template('index.html', tasks=tasks)

#Route để hiển thị danh sách công việc
@app.route('/index')
def index():
    username = session['username']
    tasks = get_tasks()
    return render_template('index.html', tasks=tasks)
# Route logout
@app.route('/logout')
def logout():
    # Xóa thông tin đăng nhập từ session
    session.pop('username', None)
    session.pop('last_login_time', None)
    return redirect(url_for('login'))
# Route để thêm công việc mới

@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    description = request.form['description'] 
    add_task(name, description)
    return redirect(url_for('index'))
# Route để cập nhật trạng thái công việc
@app.route('/update/<int:task_id>/<new_status>')
def update(task_id, new_status):
    update_task_status(task_id, new_status)
    return redirect(url_for('index'))


# Route để xóa công việc
@app.route('/delete/<int:task_id>')
def delete(task_id):
    delete_task(task_id)
    return redirect(url_for('index'))


# Route để xem chi tiết công việc
@app.route('/task/<int:task_id>')
def view_task(task_id):
    try:
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        task = cursor.fetchone()
        if task:
            logging.info(f"Viewed task details: Task ID {task_id}")
            return render_template('view_task.html', task=task)
        else:
            flash("Task not found.", 'error')
            logging.warning(f"Attempted to view non-existent task: Task ID {task_id}")
            return redirect(url_for('index'))
        # return render_template('view_task.html', task=task)
    except Exception as e:
        flash(f"Error fetching task details: {str(e)}", 'error')
        logging.error(f"Error fetching task details: {str(e)}")
        return redirect(url_for('index'))


# Route để chỉnh sửa thông tin công việc
@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if request.method == 'GET':
        try:
            cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
            task = cursor.fetchone()
            if task:
                logging.info(f"Editing task: Task ID {task_id}")
                return render_template('edit_task.html', task=task)
            else:
                flash("Task not found.", 'error')
                logging.warning(f"Attempted to edit non-existent task: Task ID {task_id}")
                return redirect(url_for('index'))
            # return render_template('edit_task.html', task=task)
        except Exception as e:
            flash(f"Error fetching task details: {str(e)}", 'error')
            logging.error(f"Error fetching task details: {str(e)}")
            return redirect(url_for('index'))
    elif request.method == 'POST':
        try:
            name = request.form['name']
            description = request.form['description']
            status = request.form['status']
            cursor.execute('''
                UPDATE tasks
                SET name = ?, description = ?, status = ?
                WHERE id = ?
            ''', (name, description, status, task_id))
            conn.commit()
            logging.info(f"Task updated: Task ID {task_id}")
            return redirect(url_for('index'))
        except Exception as e:
            flash(f"Error updating task: {str(e)}", 'error')
            logging.error(f"Error updating task: {str(e)}")
            return redirect(url_for('index'))
#Hàm gửi tin nhắn nhắc nhở
# @app.route('/send_reminder/<int:task_id>')
# def send_reminder(task_id):
#     # Lấy thông tin công việc từ cơ sở dữ liệu
#     task = Task.query.get(task_id)

#     if task:
#         # Tính thời gian nhắc nhở (ví dụ: 1 giờ trước deadline)
#         reminder_time = task.deadline - timedelta(hours=1)

#         # Kiểm tra xem thời gian nhắc nhở đã đến chưa
#         if datetime.now() >= reminder_time:
#             # Chuẩn bị nội dung email
#             subject = f'Nhắc nhở: {task.name}'
#             body = render_template('reminder_email.html', task=task)

#             # Gửi email
#             send_email(task.user.email, subject, body)

#             return 'Email nhắc nhở đã được gửi.'
#         else:
#             return 'Chưa đến thời gian nhắc nhở.'
#     else:
#         return 'Công việc không tồn tại.'
    
#Chức năng gửi email:
# def send_email(to, subject, body):
#     message = Message(subject, recipients=[to], html=body)
#     mail.send(message)

if __name__ == '__main__':
    app.run(debug=True)
