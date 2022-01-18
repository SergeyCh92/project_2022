import sqlalchemy as sq
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from settings import USER, PASSWORD, HOST, PORT, BASE_NAME, SUBD


# Устанавливаем соединение с postgres
connection = psycopg2.connect(user=USER, password=PASSWORD)
connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

# Создаем курсор для выполнения операций с базой данных
cursor = connection.cursor()
try:
    sql_create_database = cursor.execute(f'create database {BASE_NAME};')
except psycopg2.errors.DuplicateDatabase:
    pass
# Закрываем соединение
cursor.close()
connection.close()

DB = f'{SUBD}://{USER}:{PASSWORD}@{HOST}:{PORT}/{BASE_NAME}'
engine = sq.create_engine(DB)
connection = engine.connect()
connection.execute('''create table if not exists list_users(
id serial PRIMARY KEY,
id_user_vk INT NOT NULL,
name_user VARCHAR(70) NOT NULL,
id_questioner INT NOT NULL
);''')


def select_data(user_id):
    list_id_users = connection.execute(f'''SELECT id_user_vk FROM list_users
                                           WHERE id_questioner = {user_id};''').fetchall()
    return list_id_users


def insert_data(id_user_vk, name_user, id_questioner):
    connection.execute(f'''INSERT INTO list_users(id_user_vk, name_user, id_questioner)
                           VALUES
                           ('{id_user_vk}', '{name_user[0]['first_name']} {name_user[0]['last_name']}', {id_questioner})''')
