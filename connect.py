import pyodbc
import urllib  # Import the urllib module

# Thay đổi các thông tin kết nối dựa trên cấu hình của bạn
def create_connection():
    server = r'DESKTOP-CSG7S4C\SQLEXPRESS'
    database = 'quanlycongviec'
    username = ''
    password = ''

    # Chuỗi kết nối
    connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

    # Kết nối đến SQL Server
    conn = pyodbc.connect(connection_string)

    return conn
