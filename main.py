from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.redis import RedisStorage
from database.config_reader import config
from database.model_user.model_user import Place
from database.models import add_place_into_db, get_place_from_db, ModelWrite, delete_place_from_db, get_place_for_rewrite, rewrite_place_from_db, get_place_from_db_without_point
from database.messega_user.text_massege import text_in_card, greeting
import asyncio
from random import randint

#from watchgod import run_process


class Form(StatesGroup):
    title = State()
    address = State()
    photo = State()
    link = State()
    rewrite_title = State()
    rewrite_address = State()
    rewrite_photo = State()
    rewrite_link = State()
    rewrite_point = State()
    rewrite_wait = State()
    show = State()


redis_url = config.redis_url
token = config.bot_token.get_secret_value()
bot = Bot(token=token)
storage = RedisStorage.from_url(redis_url)
dp = Dispatcher(storage=storage)

key = [
    [KeyboardButton(text='Добавить место')],
    [KeyboardButton(text='Показать мой список')],
    [KeyboardButton(text='Куда сходить?')]
]


def get_delete_inline(place_id: int):
    key = [
        [InlineKeyboardButton(
            text='Удалить', callback_data=f'delete_{place_id}'
        )],
        [InlineKeyboardButton(
            text='Изменить', callback_data=f'rewrite_{place_id}'
        )]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=key)
    return keyboard


@dp.message(Command('start'))
async def start(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(keyboard=key, resize_keyboard=True)
    name = message.from_user.full_name
    await message.answer(greeting(name), reply_markup=keyboard, parse_mode=ParseMode.HTML)
    await state.clear()


@dp.message(F.text == 'Куда сходить?')
async def what_going(message: Message):
    keyboard = ReplyKeyboardMarkup(keyboard=key, resize_keyboard=True)
    user_id = message.from_user.id
    data: list[ModelWrite] = get_place_from_db_without_point(str(user_id))
    if len(data) != 0:
        number = randint(0, len(data)-1)
        place = data[number]
        await message.answer_photo(photo=place.photo_id, caption=text_in_card(place.title, place.address, place.link, place.point), reply_markup=keyboard, parse_mode=ParseMode.HTML)
    else:
        await message.answer('Вы посетили все места которые есть в вашем списке', reply_markup=keyboard)

    


@dp.message(F.text == 'Показать мой список')
async def show_my_place(message: Message):
    keyboard = ReplyKeyboardMarkup(keyboard=key, resize_keyboard=True)
    user_id = message.from_user.id
    data: list[ModelWrite] = get_place_from_db(str(user_id))
    if len(data) != 0:
        await message.answer(text='Список ваших мест', reply_markup=keyboard)
        for index, elem in enumerate(data):
            inline_button = get_delete_inline(elem.id)
            await message.answer_photo(photo=elem.photo_id, caption=text_in_card(elem.title, elem.address, elem.link, elem.point), reply_markup=inline_button, parse_mode=ParseMode.HTML)
    else:
        await message.answer('Ваш список пуст(', reply_markup=keyboard)


# Удалить место из списка
@dp.callback_query(lambda x: x.data and x.data.startswith('delete_'))
async def delete_user_place(callback: CallbackQuery):
    place_id = callback.data.removeprefix('delete_')
    place_id = int(place_id)
    delete_place_from_db(place_id)
    await callback.message.delete()


# Изменить что то в существующем месте
@dp.callback_query(lambda x: x.data and x.data.startswith('rewrite_'))
async def rewrite_user_place(callback: CallbackQuery, state: FSMContext):
    place_id = callback.data.removeprefix('rewrite_')
    place_id = int(place_id)

    data: ModelWrite = get_place_for_rewrite(place_id)
    key = [
        [KeyboardButton(text='Название')],
        [KeyboardButton(text='Адрес')],
        [KeyboardButton(text='Ссылка')],
        [KeyboardButton(text='Фото')],
        [KeyboardButton(text='Оценка')],
        [KeyboardButton(text='Назад')]
    ]

    keyboard = ReplyKeyboardMarkup(keyboard=key, resize_keyboard=True)

    await state.update_data(one_place=data.to_dict())

    await state.update_data(place_id=place_id)
    await callback.message.answer("Что вы хотите изменить?", reply_markup=keyboard)
    await state.set_state(Form.rewrite_wait)


@dp.message(F.text == 'Назад', Form.rewrite_wait)
async def exit_from_rewrite(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(keyboard=key, resize_keyboard=True)
    await message.answer('Выберите действие', reply_markup=keyboard)
    await state.clear()


@dp.message(F.text, Form.rewrite_wait)
async def rewrite_user_thing(message: Message, state: FSMContext):
    if message.text == "Название":
        key = [[KeyboardButton(text='Назад')]]
        keyboard = ReplyKeyboardMarkup(keyboard=key, resize_keyboard=True)
        await message.reply('Введите новое название', reply_markup=keyboard)
        await state.set_state(Form.rewrite_title)
    elif message.text == 'Адрес':
        key = [[KeyboardButton(text='Назад')]]
        keyboard = ReplyKeyboardMarkup(keyboard=key, resize_keyboard=True)
        await message.reply('Введите новый адрес', reply_markup=keyboard)
        await state.set_state(Form.rewrite_address)
    elif message.text == 'Ссылка':
        key = [[KeyboardButton(text='Назад')]]
        keyboard = ReplyKeyboardMarkup(keyboard=key, resize_keyboard=True)
        await message.reply('Введите новую ссылку', reply_markup=keyboard)
        await state.set_state(Form.rewrite_link)
    elif message.text == 'Фото':
        key = [[KeyboardButton(text='Назад')]]
        keyboard = ReplyKeyboardMarkup(keyboard=key, resize_keyboard=True)
        await message.reply('Отправьте новое фото', reply_markup=keyboard)
        await state.set_state(Form.rewrite_photo)
    elif message.text == 'Оценка':
        key = [
            [KeyboardButton(text='1'), KeyboardButton(text='2'), KeyboardButton(
                text='3'), KeyboardButton(text='4'), KeyboardButton(text='5')],
            [KeyboardButton(text='Назад')]
        ]
        keyboard = ReplyKeyboardMarkup(keyboard=key, resize_keyboard=True)
        await message.reply('Оцените', reply_markup=keyboard)
        await state.set_state(Form.rewrite_point)
    else:
        await message.reply('Неккоретный ввод')

# Изменение названия


@dp.message(F.text != 'Назад', Form.rewrite_title)
async def rewrite_title_place(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(keyboard=key, resize_keyboard=True)
    data: dict = await state.get_data()
    data: ModelWrite = ModelWrite.from_dict(data.get('one_place'))
    data.title = message.text
    rewrite_place_from_db(data)
    await message.answer('Вы успешно изменили имя', reply_markup=keyboard)
    await state.clear()


@dp.message(F.text == 'Назад', Form.rewrite_title)
async def exit_from_rewrite_title(message: Message, state: FSMContext):
    data: dict = await state.get_data()
    data: ModelWrite = ModelWrite.from_dict(data.get('one_place'))
    key = [
        [KeyboardButton(text='Название')],
        [KeyboardButton(text='Адрес')],
        [KeyboardButton(text='Ссылка')],
        [KeyboardButton(text='Фото')],
        [KeyboardButton(text='Оценка')],
        [KeyboardButton(text='Назад')]
    ]

    keyboard = ReplyKeyboardMarkup(keyboard=key, resize_keyboard=True)
    await message.answer('Что хотите изменить?', reply_markup=keyboard)
    await state.set_state(Form.rewrite_wait)
# Конец изменения названия места


# Изменение адреса места
@dp.message(F.text != 'Назад', Form.rewrite_address)
async def rewrite_address_place(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(keyboard=key, resize_keyboard=True)
    data: dict = await state.get_data()
    data: ModelWrite = ModelWrite.from_dict(data.get('one_place'))
    data.address = message.text
    rewrite_place_from_db(data)
    await message.answer('Вы успешно изменили адрес', reply_markup=keyboard)
    await state.clear()


@dp.message(F.text == 'Назад', Form.rewrite_address)
async def exit_from_rewrite_title(message: Message, state: FSMContext):
    data: dict = await state.get_data()
    data: ModelWrite = ModelWrite.from_dict(data.get('one_place'))
    key = [
        [KeyboardButton(text='Название')],
        [KeyboardButton(text='Адрес')],
        [KeyboardButton(text='Ссылка')],
        [KeyboardButton(text='Фото')],
        [KeyboardButton(text='Оценка')],
        [KeyboardButton(text='Назад')]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=key, resize_keyboard=True)
    await message.answer('Что хотите изменить?', reply_markup=keyboard)
    await state.set_state(Form.rewrite_wait)
# Конец изменения адреса места


# Изменение ссылки места
@dp.message(F.text != 'Назад', Form.rewrite_link)
async def rewrite_link_place(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(keyboard=key, resize_keyboard=True)
    data: dict = await state.get_data()
    data: ModelWrite = ModelWrite.from_dict(data.get('one_place'))
    data.link = message.text
    rewrite_place_from_db(data)
    await message.answer('Вы успешно изменили ссылку', reply_markup=keyboard)
    await state.clear()


@dp.message(F.text == 'Назад', Form.rewrite_link)
async def exit_from_rewrite_title(message: Message, state: FSMContext):
    data: dict = await state.get_data()
    data: ModelWrite = ModelWrite.from_dict(data.get('one_place'))
    key = [
        [KeyboardButton(text='Название')],
        [KeyboardButton(text='Адрес')],
        [KeyboardButton(text='Ссылка')],
        [KeyboardButton(text='Фото')],
        [KeyboardButton(text='Оценка')],
        [KeyboardButton(text='Назад')]
    ]

    keyboard = ReplyKeyboardMarkup(keyboard=key, resize_keyboard=True)
    await message.answer('Что хотите изменить?', reply_markup=keyboard)
    await state.set_state(Form.rewrite_wait)
# Конец изменения ссылки места


# Изменение фото места
@dp.message(F.text != 'Назад', Form.rewrite_photo)
async def rewrite_photo_place(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(keyboard=key, resize_keyboard=True)
    data: dict = await state.get_data()
    data: ModelWrite = ModelWrite.from_dict(data.get('one_place'))
    photo = message.photo[-1]
    data.photo_id = photo.file_id
    rewrite_place_from_db(data)
    await message.answer('Вы успешно изменили фото', reply_markup=keyboard)
    await state.clear()


@dp.message(F.text == 'Назад', Form.rewrite_photo)
async def exit_from_rewrite_title(message: Message, state: FSMContext):
    data: dict = await state.get_data()
    data: ModelWrite = ModelWrite.from_dict(data.get('one_place'))
    key = [
        [KeyboardButton(text='Название')],
        [KeyboardButton(text='Адрес')],
        [KeyboardButton(text='Ссылка')],
        [KeyboardButton(text='Фото')],
        [KeyboardButton(text='Оценка')],
        [KeyboardButton(text='Назад')]
    ]

    keyboard = ReplyKeyboardMarkup(keyboard=key, resize_keyboard=True)
    await message.answer('Что хотите изменить?', reply_markup=keyboard)
    await state.set_state(Form.rewrite_wait)
# Конец изменения фото места


# Изменение оценки места
@dp.message(F.text != 'Назад', Form.rewrite_point)
async def rewrite_address_place(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(keyboard=key, resize_keyboard=True)
    data: dict = await state.get_data()
    data: ModelWrite = ModelWrite.from_dict(data.get('one_place'))
    if message.text in '12345' and len(message.text) < 2:
        data.point = message.text
    else:
        await message.reply('Некоректные данные, попробуйте еще раз')
    rewrite_place_from_db(data)
    await message.answer('Вы успешно изменили оценку', reply_markup=keyboard)
    await state.clear()


@dp.message(F.text == 'Назад', Form.rewrite_point)
async def exit_from_rewrite_title(message: Message, state: FSMContext):
    data: dict = await state.get_data()
    data: ModelWrite = ModelWrite.from_dict(data.get('one_place'))
    key = [
        [KeyboardButton(text='Название')],
        [KeyboardButton(text='Адрес')],
        [KeyboardButton(text='Ссылка')],
        [KeyboardButton(text='Фото')],
        [KeyboardButton(text='Оценка')],
        [KeyboardButton(text='Назад')]
    ]

    keyboard = ReplyKeyboardMarkup(keyboard=key, resize_keyboard=True)
    await message.answer('Что хотите изменить?', reply_markup=keyboard)
    await state.set_state(Form.rewrite_wait)
# Конец изменения оценки места


# Добавление нового места
@dp.message(F.text == 'Добавить место')
async def add_place(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    place = Place(user_id=user_id)
    await state.update_data(place=place.to_dict())
    await message.answer("Давай добавим прикольное место! Напиши название:")
    await state.set_state(Form.title)


@dp.message(F.text, Form.title)
async def add_title(message: Message, state: FSMContext):
    data = await state.get_data()
    place = Place.from_dict(data.get('place'))
    place.title = message.text
    await state.update_data(place=place.to_dict())
    await message.answer('Теперь напиши адрес!')
    await state.set_state(Form.address)


@dp.message(F.text, Form.address)
async def add_address(message: Message, state: FSMContext):
    data = await state.get_data()
    place = Place.from_dict(data.get('place'))
    place.address = message.text
    await state.update_data(place=place.to_dict())
    await message.answer("Отлично, теперь отправь фото этого места")
    await state.set_state(Form.photo)


@dp.message(F.photo, Form.photo)
async def add_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    place = Place.from_dict(data.get('place'))
    photo = message.photo[-1]
    photo_id = photo.file_id
    place.photo_id = photo_id
    await state.update_data(place=place.to_dict())
    await message.answer('Замечательно, теперь кинь ссылку на карты или на сайт!')
    await state.set_state(Form.link)


@dp.message(F.text, Form.link)
async def add_link(message: Message, state: FSMContext):
    data = await state.get_data()
    place = Place.from_dict(data.get('place'))
    place.link = message.text
    await state.update_data(place=place.to_dict())
    keyboard = ReplyKeyboardMarkup(keyboard=key, resize_keyboard=True)
    await message.answer('Спасибо, мы добавили место', reply_markup=keyboard)
    add_place_into_db(place)
    await state.clear()


async def main():
    await dp.start_polling(bot)


# def main1():
#     asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())
    #run_process('.', main1)
