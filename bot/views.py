import telebot
from django.conf import settings
from django.http.response import HttpResponse

from telebot.types import KeyboardButton
from telebot.types import ReplyKeyboardMarkup

from bot.const import BUTTONS
from bot.const import USER_STEP

from bot.models import Orders
from bot.models import Tg_Users

from data.models import Province

from bot.services import set_lang
from bot.services import select_province
from bot.services import select_district
from bot.services import enter_first_name
from bot.services import thank_you_message
from bot.services import number_of_passengers


bot = telebot.TeleBot(settings.BOT_TOKEN)


def web_hook_view(request):
    if request.method == 'POST':
        bot.process_new_updates([telebot.types.Update.de_json(request.body.decode("utf-8"))])
        return HttpResponse(status=200)
    return HttpResponse('404 not found')


@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.chat.id
    if Tg_Users.objects.filter(user_id=user_id).exists():
        user = Tg_Users.objects.get(user_id=message.chat.id)
        lan = user.lan

        Orders.objects.get(user=user, status=False).delete()
        Tg_Users.objects.filter(user_id=message.chat.id).update(step=USER_STEP['CHOOSE_LOCATION'])

        if lan == 'uz':
            text = 'Siz turgan manzil ?'
            province = Province.objects.all().values_list('name_uz', flat=1)
        if lan == 'rus':
            province = Province.objects.all().values_list('name_ru', flat=1)
            text = 'Ваш текущий адрес ?'
        reply_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

        buttons = [KeyboardButton(text=text) for text in province]
        reply_markup.add(*buttons)

        bot.send_message(message.chat.id, text, reply_markup=reply_markup)
    else:
        Tg_Users.objects.create(
            user_id=user_id,
            lan='uz',
            step=USER_STEP['CHOOSE_LANGUAGE'])

        lan_button = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = [
            KeyboardButton(text='🇺🇿 O\'zbek'),
            KeyboardButton(text='🇷🇺 Руский')
        ]
        lan_button.add(*buttons)
        text = "Tilni tanlang:\n"
        text += "Выберите язык:"
        bot.send_message(user_id, text, reply_markup=lan_button)


@bot.message_handler(commands=['lan'])
def change_lan(message):
    user = Tg_Users.objects.get(user_id=message.chat.id)
    user.step = USER_STEP['CHOOSE_LANGUAGE']
    user.save()
    lan_button = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        KeyboardButton(text='🇺🇿 O\'zbek'),
        KeyboardButton(text='🇷🇺 Руский')
    ]

    lan_button.add(*buttons)
    text = "Tilni tanlang:\n"
    text += "Выберите язык:"
    bot.send_message(message.chat.id, text, reply_markup=lan_button)


@bot.message_handler(regexp=BUTTONS['BACK_UZ'])
def back_message_uz(message):
    user = Tg_Users.objects.get(user_id=message.chat.id)

    if user.step == USER_STEP['SELECT_DISTRICT']:
        start_message(message)
    else:
        user.step -= 2
        user.save()
        text_message(message)


@bot.message_handler(regexp=BUTTONS['BACK_RU'])
def back_message_ru(message):
    user = Tg_Users.objects.get(user_id=message.chat.id)

    if user.step == USER_STEP['SELECT_DISTRICT']:
        start_message(message)
    else:
        user.step -= 2
        user.save()
        text_message(message)


@bot.message_handler(content_types=['text', 'contact'])
def text_message(message):
    switcher = {
        USER_STEP['CHOOSE_LANGUAGE']: set_lang,
        USER_STEP['ENTER_FIRST_NAME']: enter_first_name,
        USER_STEP['CHOOSE_LOCATION']: select_province,
        USER_STEP['SELECT_DISTRICT']: select_district,
        USER_STEP['NUMBER_OF_PASSANGERS']: number_of_passengers,
        USER_STEP['THANK_YOU_MESSAGE']: thank_you_message
    }

    func = switcher.get(Tg_Users.objects.get(user_id=message.chat.id).step, lambda: start_message(message))
    func(message, bot)
