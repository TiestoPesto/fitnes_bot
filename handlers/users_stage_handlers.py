import logging

from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import executor, types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import callback_query, CallbackQuery

import config

# Переключаемся на асинхронный режим PostgreSQL
import asyncpg

from create_bot import dp, bot
from database import create_db_connection
from keyboard.users_kb import kb_location_inline, kb_agree_thankful, kb_agree_attention, kb_gender_markup, \
	kb_interest_markup, kb_process_about, kb_main, kb_cancel, kb_done, kb_watch


# Определение состояний
class Survey(StatesGroup):
	fitness_club = State()
	thankful = State()
	attention = State()
	agree = State()
	age = State()
	username = State()
	gender = State()
	interest = State()
	about = State()
	photo = State()
	done = State()


# Команда для начала диалога
# Обработчик для команды /start
# @dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
	try:
		await Survey.fitness_club.set()
		await message.answer("Рады приветствовать вас в нашем боте!"
		                     "Выбери фитнес-клуб, в который ты ходишь", reply_markup=kb_location_inline)
	except Exception as e:
		logging.exception("Ошибка в функции send_welcome")
		return None


@dp.callback_query_handler(lambda c: c.data.startswith('start'))
async def process_thankful(callback_query: types.CallbackQuery):
	try:
		await callback_query.answer()
		# Удаляем сообщение, на которое был дан ответ
		await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
		await Survey.fitness_club.set()
		await callback_query.message.answer("Рады приветствовать вас в нашем боте!"
		                     "Выбери фитнес-клуб, в который ты ходишь", reply_markup=kb_location_inline)
	except Exception as e:
		logging.exception("Ошибка в process_thankful")


@dp.callback_query_handler(lambda c: c.data.startswith('location_'), state=Survey.fitness_club)
async def process_fitness_club_inline(callback_query: types.CallbackQuery, state: FSMContext):
	try:
		await callback_query.answer()
		# Удаляем сообщение, на которое был дан ответ
		await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
		# Получаем название фитнес-клуба из callback_data, удаляя префикс и заменяя подчеркивания пробелами
		fitness_club_address = callback_query.data[len('location_'):].replace('_', ' ')
		print(fitness_club_address)
		# Создаем асинхронное соединение с базой данных
		db_conn = await create_db_connection()
		
		try:
			# Выполняем запрос к базе данных для получения club_id
			statement = "SELECT * FROM fitness_clubs WHERE address LIKE $1"
			result = await db_conn.fetchrow(statement, fitness_club_address)
			
			if result:
				club_id = result['club_id']  # Предполагая, что 'id' это имя колонки с club_id
			else:
				# Обработка ситуации, если фитнес-клуб не найден
				club_id = None
			
			# Сохраняем club_id в состояние FSM
			async with state.proxy() as data:
				data['fitness_club'] = club_id
			
			# Переходим к следующему вопросу в опросе
			await Survey.next()
			await callback_query.message.answer("Как же у тебя отлично получается. "
			                                    "Помогу найти тебе пару, можно я задам тебе пару вопросов?",
			                                    reply_markup=kb_agree_thankful)
		except Exception as e:
			logging.error(f"Произошла ошибка при поиске club_id: {e}, тип ошибки: {type(e).__name__}")
		finally:
			if db_conn:
				await db_conn.close()
	except Exception as e:
		logging.exception("Ошибка в process_fitness_club_inline")


@dp.callback_query_handler(lambda c: c.data.startswith('agree_thankful'), state=Survey.thankful)
async def process_thankful(callback_query: types.CallbackQuery, state: FSMContext):
	try:
		await callback_query.answer()
		# Удаляем сообщение, на которое был дан ответ
		await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
		await Survey.agree.set()
		await callback_query.message.answer("Помни, что в интернете люди могут выдавать себя за других. "
		                                    "Бот не запрашивает личные данные и не идентифицирует пользователей по паспортным данным. "
		                                    "Продолжая использование бота ты соглашаешься с использованием бота на свой страх и риск.",
		                                    reply_markup=kb_agree_attention)
	except Exception as e:
		logging.exception("Ошибка в process_thankful")


@dp.callback_query_handler(lambda c: c.data.startswith('agree_attention'), state=Survey.agree)
async def process_agree_attention(callback_query: types.CallbackQuery, state: FSMContext):
	try:
		await callback_query.answer()
		# Удаляем сообщение, на которое был дан ответ
		await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
		await Survey.next()
		await callback_query.message.answer("Сколько тебе лет?")
	except Exception as e:
		logging.exception("Ошибка в process_agree_attention")


@dp.message_handler(state=Survey.age)
async def process_age(message: types.Message, state: FSMContext):
	try:
		# Удаляем сообщение с запросом ввода имени
		await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
		await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
		age = message.text
		
		if not age.isdigit():
			await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
			await message.answer("Пожалуйста, введите корректное число Вашего возраста.",
			                     reply_markup=kb_cancel)
			return
		
		age = int(age)
		if not 18 <= age <= 70:
			await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
			await message.answer("Пожалуйста, укажите возраст от 18 до 70 лет.", reply_markup=kb_cancel)
			return
		async with state.proxy() as data:
			data['age'] = int(message.text)
		await Survey.next()
		await message.answer("Теперь напиши, как к тебе обращаться?")
	except Exception as e:
		logging.exception("Ошибка в process_age")


@dp.message_handler(state=Survey.username)
async def process_username(message: types.Message, state: FSMContext):
	try:
		# Удаляем сообщение с запросом ввода имени
		await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
		await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
		name = message.text
		if name.isdigit() or len(name) > 10:
			await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
			await message.answer("Пожалуйста, введите корректное имя.", reply_markup=kb_cancel)
			return
		
		async with state.proxy() as data:
			data['username'] = message.text
		await Survey.next()
		await message.answer("Теперь определимся с полом", reply_markup=kb_gender_markup)
	except Exception as e:
		logging.exception("Ошибка в process_username")


@dp.callback_query_handler(lambda c: c.data.startswith('gender_'), state=Survey.gender)
async def process_gender(callback_query: types.CallbackQuery, state: FSMContext):
	try:
		# Удаляем сообщение, на которое был дан ответ
		await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
		# Получаем название фитнес-клуба из callback_data, удаляя префикс и заменяя подчеркивания пробелами
		gender = callback_query.data[len('gender_'):].replace('_', ' ')
		print(gender)
		async with state.proxy() as data:
			data['gender'] = gender
		await Survey.interest.set()
		
		await callback_query.message.answer("Кто тебе интересен?", reply_markup=kb_interest_markup)
	except Exception as e:
		logging.exception("Ошибка в process_gender")


@dp.callback_query_handler(lambda c: c.data.startswith('interest_'), state=Survey.interest)
async def process_interest(callback_query: types.CallbackQuery, state: FSMContext):
	try:
		# Удаляем сообщение, на которое был дан ответ
		await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
		# Получаем название фитнес-клуба из callback_data, удаляя префикс и заменяя подчеркивания пробелами
		interest = callback_query.data[len('interest_'):].replace('_', ' ')
		print(interest)
		async with state.proxy() as data:
			data['interest'] = interest
		await Survey.about.set()
		await callback_query.message.answer("Расскажи о себе и кого хочешь найти, "
		                     "чем предлагаешь заняться. Это поможет лучше подобрать тебе компанию.",
		                     reply_markup=kb_process_about)
	except Exception as e:
		logging.exception("Ошибка в process_interest")


# Обработчик колбэк кнопки в состоянии AboutMe
@dp.callback_query_handler(lambda c: c.data.startswith('aabout_'), state=Survey.about)
async def process_about_me_invisible(callback_query: types.CallbackQuery, state: FSMContext):
	try:
		await callback_query.answer()
		# Удаляем сообщение, на которое был дан ответ
		await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
		# Получаем название фитнес-клуба из callback_data, удаляя префикс и заменяя подчеркивания пробелами
		about = callback_query.data[len('aabout_'):].replace('_', ' ')
		print(about)
		async with state.proxy() as data:
			data['about'] = about
		await Survey.photo.set()
		await callback_query.message.answer("Спасибо за информацию о себе!\n"
		                           "Теперь пришли фото, его будут видеть другие пользователи.")
	except Exception as e:
		logging.exception("Ошибка в process_about_me_invisible")

# @dp.message_handler(state=Survey.about)
# async def process_about(message: types.Message, state: FSMContext):
# 	try:
# 		async with state.proxy() as data:
# 			data['about'] = message.text
# 		await Survey.photo.set()
# 		await message.answer("Теперь пришли фото, его будут видеть другие пользователи")
# 	except Exception as e:
# 		logging.exception("Ошибка в process_about")


@dp.message_handler(content_types=['photo'], state=Survey.photo)
async def process_photo(message: types.Message, state: FSMContext):
	try:
		# Удаляем сообщение с запросом ввода имени
		await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
		await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
		async with state.proxy() as data:
			data['photo'] = message.photo[-1].file_id
		
		user_id = message.from_user.id
		profile_text = await profile_tab(data)
		await bot.send_photo(chat_id=user_id, caption=profile_text, photo=data['photo'], reply_markup=kb_done,
		                     parse_mode=types.ParseMode.HTML)
		# await message.answer(
		# 	"Твоя анкета:\nФото: {photo}\nИмя: {username}\nВозраст: {age}\nКлуб: {fitness_club}\nО себе: {about}".format(
		# 		**data), reply_markup=kb_done)
		await Survey.done.set()
	except Exception as e:
		logging.exception("Ошибка в process_photo")


# Обработчик колбэк кнопки в состоянии AboutMe
@dp.callback_query_handler(lambda c: c.data.startswith('done'), state=Survey.done)
async def process_done(query: types.CallbackQuery, state: FSMContext):
	try:
		# Удаляем сообщение, на которое был дан ответ
		await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
		await query.answer()
		async with state.proxy() as data:
			# Сразу после сохранения фото, вызываем функцию сохранения данных в базу
			# Передаем копию данных, чтобы избежать проблем с асинхронностью
			await save_user_data(data.as_dict())
		await state.finish()
		await query.message.answer("Спасибо, теперь вы можете посмотреть анкеты пользователей.",
		                           reply_markup=kb_watch)
	except Exception as e:
		logging.exception("Ошибка в process_done")


# Ловим отмену
@dp.callback_query_handler(Text(equals='cancel', ignore_case=True), state="*")
# @dp.callback_query_handler(lambda c: c.data == 'cancel')
async def cancel_registration(callback: types.CallbackQuery, state: FSMContext):
	try:
		
		current_state = await state.get_state()
		# print(current_state)
		if current_state is not None:
			await state.finish()
			
			# Удаляем сообщение, на которое был дан ответ
			await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
			
			await callback.message.answer(
				"Регистрация отменена. Вы можете начать заново нажав кнопку Зарегистрироваться",
				reply_markup=kb_main)
		await callback.answer()
	
	except Exception as e:
		# Логирование исключения может помочь в диагностике проблем
		logging.error(f"Error in cancel_registration: {e}")
		
		await bot.send_message(callback.from_user.id, 'Что-то пошло не так. Напишите нам @sms_supportbot')


# Функция для сохранения данных в базу данных
async def save_user_data(data):
	db_conn = None
	try:
		db_conn = await create_db_connection()
		if db_conn is None or db_conn.is_closed():  # Проверяем, открыто ли соединение
			print("test db_conn")
			db_conn = await create_db_connection()  # Повторно открываем соединение, если оно закрыто
		# Выполнение запроса к БД
		await db_conn.execute('''
            INSERT INTO users(username, age, gender, interest, about, fitness_club, photo_url)
            VALUES($1, $2, $3, $4, $5, $6, $7)
        ''', data['username'], data['age'], data['gender'], data['interest'], data['about'],
		                      data['fitness_club'], data['photo'])
		print("Данные пользователя успешно сохранены.")
	except Exception as e:
		logging.error(f"Произошла ошибка сохранения в БД: {e}")
	finally:
		if db_conn:
			await db_conn.close()


async def profile_tab(data):
	try:
		# Подготовьте текстовое описание профиля
		profile_text = (
			f"<i>Имя:</i> <b>{data['username']}</b>\n"
			f"<i>Возраст:</i>  <b>{data['age']} лет.</b>\n"
			f"<i>Клуб:</i>  <b>{data['fitness_club']}</b>\n"
			f"<i>О себе: </i> <b>{data['about']}</b>\n"
		)
		
		return profile_text
	except Exception as e:
		# Логирование исключения может помочь в диагностике проблем
		logging.error(f"Error in profile_tab: {e}")


def reg_handlers_client(dp: Dispatcher):
	dp.register_message_handler(send_welcome, commands=['start'])
# dp.register_callback_query_handler(process_fitness_club, state=Survey.fitness_club)
