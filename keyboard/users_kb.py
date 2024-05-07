from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

kb_location_inline = InlineKeyboardMarkup(row_width=1).add(
	InlineKeyboardButton("Спорт-Стиль, Чебрикова 38", callback_data='location_Чебрикова_38'),
	InlineKeyboardButton("Спорт-Стиль, Кирпичная 24 б", callback_data='location_Кирпичная_24_б'),
	InlineKeyboardButton("Спорт-Стиль, Свердлова 55", callback_data='location_Свердлова_55')
)

kb_agree_thankful = types.InlineKeyboardMarkup() \
	.add(types.InlineKeyboardButton("Хорошо", callback_data='agree_thankful'))

kb_agree_attention = types.InlineKeyboardMarkup() \
	.add(types.InlineKeyboardButton("Хорошо", callback_data='agree_attention')
         )

kb_gender_markup = InlineKeyboardMarkup(row_width=2).add(
	InlineKeyboardButton("Я парень", callback_data='gender_Парень'),
	InlineKeyboardButton("Я девушка", callback_data='gender_Дeвушка'))

kb_interest_markup = InlineKeyboardMarkup(row_width=2).add(
	InlineKeyboardButton("Парни", callback_data='interest_Парни'),
	InlineKeyboardButton("Девушки", callback_data='interest_Девушки'),
	InlineKeyboardButton("Все равно", callback_data='interest_Без_разницы'))

kb_process_about = InlineKeyboardMarkup(row_width=2).add(
	InlineKeyboardButton("Пропустить", callback_data='aabout_Без_разницы'),
	InlineKeyboardButton("Я человек - загадка", callback_data='aabout_Я_человек_-_загадка'))

kb_done = types.InlineKeyboardMarkup() \
	.add(types.InlineKeyboardButton("Хорошо", callback_data='done')) \
	.add(types.InlineKeyboardButton("Отмена", callback_data='cancel'))

kb_main = types.InlineKeyboardMarkup() \
	.add(types.InlineKeyboardButton("Зарегистрироваться", callback_data='start'))


kb_cancel = types.InlineKeyboardMarkup() \
	.add(types.InlineKeyboardButton("Отмена", callback_data='cancel'))

kb_watch = types.InlineKeyboardMarkup() \
	.add(types.InlineKeyboardButton("Смотреть анкеты", callback_data='watch'))
