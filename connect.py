import pyodbc

# Thay đổi các thông tin kết nối dựa trên cấu hình của bạn
def create_connection():
    server = '.\SQLEXPRESS04'
    database = 'quanlycongviec'
    username = ''
    password = ''

    # Chuỗi kết nối
    connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

    # Kết nối đến SQL Server
    conn = pyodbc.connect(connection_string)

    return conn