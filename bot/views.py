import telebot
from datetime import datetime
from telebot.types import KeyboardButton
from telebot.types import ReplyKeyboardMarkup

from django.conf import settings
from django.http.response import HttpResponse


from bot.const import BUTTONS
from bot.const import USER_STEP
from bot.const import CHANNEL_ID

from bot.models import Orders
from bot.models import Tg_Users
from bot.services import enter_first_name, select_district


from  data.models import District
from  data.models import Province


bot = telebot.TeleBot(settings.BOT_TOKEN)


def web_hook_view(request):
    if request.method == 'POST':
        # print('/'*88)
        bot.process_new_updates([telebot.types.Update.de_json(request.body.decode("utf-8"))])
        return HttpResponse(status=200)
    return HttpResponse('404 not found')


@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        if Tg_Users.objects.filter(user_id=message.chat.id).exists():
            Tg_Users.objects.filter(user_id=message.chat.id).update(step=0)

            text = 'Siz turgan joy ?'
            province = Province.objects.all().values_list('name', flat=True)
            reply_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

            buttons = [KeyboardButton(text=text) for text in province]
            reply_markup.add(*buttons)

            bot.send_message(message.chat.id, text, reply_markup=reply_markup)
        else:
            print('/'*88)
            Tg_Users.objects.create(user_id=message.chat.id, step=USER_STEP['ENTER_FIRST_NAME'])

            text = 'Salom Mini burget bot ga xush kelibsiz!!!\n\n'
            text += 'Ismingizni kiriting:'
            bot.send_message(message.chat.id, text)
    except Exception as e:
        print(e)


@bot.message_handler(content_types=['text'])
def text_message(message):
    switcher = {
        USER_STEP['ENTER_FIRST_NAME']: enter_first_name,
        USER_STEP['CHOOSE_LOCATION']: select_district
    }
    print(Tg_Users.objects.get(user_id=message.chat.id).step)
    func = switcher.get(Tg_Users.objects.get(user_id=message.chat.id).step, lambda: start_message(message))
    func(message, bot)
