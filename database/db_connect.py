import logging
import asyncpg
import config


async def create_db_connection():
	connection = None
	try:
		# Используем await для получения соединения, которое поддерживает асинхронный контекстный менеджер
		connection = await asyncpg.connect(user=config.DB_USER,
		                                   password=config.DB_PASS,
		                                   database=config.DB_NAME,
		                                   host=config.DB_HOST,
		                                   port=config.DB_PORT)
		print("Подключение к базе данных успешно установлено.")
		return connection
	except Exception as e:
		logging.error(f"Ошибка подключения к базе данных: {e}")
