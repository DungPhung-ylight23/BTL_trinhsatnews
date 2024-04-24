import sqlite3

def create_table():
    connection = sqlite3.connect("trinhsatnews.db")
    cursor = connection.cursor()
    # Tạo bảng 'news' với các cột 'id', 'title', 'description', 'content', 'url'
    cursor.execute('''CREATE TABLE news (
                        id INTEGER PRIMARY KEY,
                        title TEXT NOT NULL,
                        description TEXT,
                        content TEXT,
                        url TEXT
                    )''')

    # Lưu thay đổi và đóng kết nối
    connection.commit()
    connection.close()