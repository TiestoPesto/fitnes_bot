import config
from create_bot import dp
from handlers import users_stage_handlers

users_stage_handlers.reg_handlers_client(dp)

async def on_startup(_):
	await dp.bot.send_message(config.ADMIN_ID, 'Бот запущен! И готов работать')
	


if __name__ == '__main__':
	from aiogram import executor
	executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
