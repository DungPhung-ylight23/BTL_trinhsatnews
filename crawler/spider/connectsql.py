import mysql.connector
from mysql.connector import Error
import yaml

config_file = "crawler_config.yml"

# class Article:
#     def __init__(self, title, description, content, url):
#         self.title = title
#         self.description = description
#         self.content = content
#         self.url = url




def __init__(self, host, user, password, database):
    self.host = host
    self.user = user
    self.password = password
    self.database = database                


def read_database_config(config_file):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config['database']

def get_connection():
    try:
        database_config = read_database_config(config_file)
        connection = mysql.connector.connect(
            host=database_config['host'],
            user=database_config['username'],
            password=database_config['password'],
            database=database_config['database']
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except Error as e:
        print("Error while connecting to MySQL", e)
        return None
    
def insert_article(self, article):
    sql = "INSERT INTO news (title, description, content, url) VALUES (%s, %s, %s, %s)"
    val = (article.title, article.description,
            article.content, article.url)

    cursor = self.connection.cursor()
    cursor.execute(sql, val)
    self.connection.commit()
    cursor.close()
