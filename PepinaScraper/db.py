import mysql.connector as mc
from PepinaScraper.read_config import read_db_config

class DB():
	def __init__(self):
		mysql_config = read_db_config('config.ini', 'mysql')
		print(mysql_config)
		try:
			self.conn = mc.connect(**mysql_config)
		except mc.Error as e:
			print(e)
			exit()


	def create_shoes_table(self):
		sql = """
			CREATE TABLE IF NOT EXISTS shoes(
				id INT AUTO_INCREMENT PRIMARY KEY,
				brand VARCHAR(100) NOT NULL,
				price FLOAT NOT NULL,
				color VARCHAR(50) NOT NULL
			);
		"""

		with self.conn.cursor() as cursor:
			cursor.execute(sql)
			self.conn.commit()
			print(f'Table shoes created!')

	def drop_shoes_table(self):
		sql = "DROP TABLE IF EXISTS shoes";

		with self.conn.cursor() as cursor:
			cursor.execute(sql)
			self.conn.commit()

	def insert_rows(self, rows_data):
		sql = """
			INSERT IGNORE INTO shoes
			(title, pub_date, content)
			VALUES ( %s, %s, %s)
		"""

		with self.conn.cursor() as cursor:
			cursor.executemany(sql, rows_data)
			self.conn.commit()

	def insert_row(self, row_data):
		sql = """
			INSERT IGNORE INTO shoes
				(title, pub_date, content)
				VALUES ( %s, %s, %s)
		"""

		with self.conn.cursor(prepared=True) as cursor:
			cursor.execute(sql, tuple(row_data.values()))
			self.conn.commit()

	def select_all_data(self):
		sql = "SELECT id, title, pub_date, content FROM  shoes"

		with self.conn.cursor() as cursor:
			cursor.execute(sql)
			result = cursor.fetchall()

		return result

	def get_last_updated_date(self):
		sql = 'SELECT MAX(updated_at) AS "Max Date" FROM shoes;'
		with self.conn.cursor() as cursor:
			cursor.execute(sql)
			result = cursor.fetchone()

		if result:
			return result[0]
		else:
			raise ValueError('No data in table')

	def get_column_names(self):
		sql = "SELECT id, title, pub_date, content FROM  shoes LIMIT 1;"

		with self.conn.cursor() as cursor:
			cursor.execute(sql)
			result = cursor.fetchone()

		return cursor.column_names

if __name__ == '__main__':
	db = DB()

	# db.get_column_names()
	res = db.get_last_updated_date()
	print(res)
