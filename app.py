import logging
import os

from logging.handlers import TimedRotatingFileHandler

from flask import Flask, render_template, request, redirect, url_for, flash

from connect import create_connection  # Import hàm tạo kết nối

# Tạo thư mục logs nếu nó không tồn tại
if not os.path.exists('logs'):
    os.makedirs('logs')

# Cấu hình logging
logging.basicConfig(filename='logs/app.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

app = Flask(__name__)

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


# Route để hiển thị danh sách công việc
@app.route('/')
def index():
    tasks = get_tasks()
    return render_template('index.html', tasks=tasks)


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


if __name__ == '__main__':
    app.run(debug=True)
