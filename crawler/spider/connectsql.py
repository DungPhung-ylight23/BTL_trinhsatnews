
import sqlite3


def connect_to_sqlite(database_file):
    try:
        # Kết nối đến cơ sở dữ liệu SQLite
        connection = sqlite3.connect(database_file)
        print("Connected to SQLite database")
        return connection
    except sqlite3.Error as e:
        print("Error while connecting to SQLite:", e)
        return None


def is_url_exists(connection, url):
    try:
        cursor = connection.cursor()
        # Thực hiện truy vấn SELECT để kiểm tra xem URL đã tồn tại trong cơ sở dữ liệu hay chưa
        sql = "SELECT COUNT(*) FROM article WHERE url = ?"
        cursor.execute(sql, (url,))
        # Lấy kết quả từ truy vấn
        count = cursor.fetchone()[0]
        # Nếu số lượng bản ghi có URL tương tự lớn hơn 0, tức là URL đã tồn tại
        return count > 0
    except sqlite3.Error as e:
        print("Error while checking URL existence:", e)
        return False

def insert_article(connection, article):
    try:
        cursor = connection.cursor()
        # Thực hiện truy vấn INSERT để chèn dữ liệu vào bảng "article"
        sql = """INSERT INTO article (id, title, url, image_url, author, content, created_at, sentiment, is_fake)
                 VALUES (?,?, ?, ?, ?, ?, ?, ?, ?)"""
        # Truyền đúng số lượng tham số vào hàm execute()
        cursor.execute(sql, (article.id, article.title, article.url, article.image_url,
                       article.author, article.content, article.created_at, article.sentiment, article.is_fake))
        # Lưu thay đổi vào cơ sở dữ liệu
        connection.commit()
        print("Article inserted successfully.")
    except sqlite3.Error as e:
        print("Error while inserting article:", e)
