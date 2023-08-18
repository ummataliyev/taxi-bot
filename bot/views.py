import telebot
from telebot.types import KeyboardButton
from telebot.types import ReplyKeyboardMarkup

from django.conf import settings
from django.http.response import HttpResponse


from bot.const import USER_STEP
from bot.const import BUTTONS

from bot.models import Tg_Users, Orders
from bot.services import enter_first_name, select_province, number_of_passengers, select_district, thank_you_message


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
            user = Tg_Users.objects.get(user_id=message.chat.id)
            try:
                Orders.objects.get(user=user, status=False).delete()
            except:
                pass
            Tg_Users.objects.filter(user_id=message.chat.id).update(step=2)

            text = 'Siz turgan joy ?'
            province = Province.objects.all().values_list('name', flat=True)
            reply_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

            buttons = [KeyboardButton(text=text) for text in province]
            reply_markup.add(*buttons)

            bot.send_message(message.chat.id, text, reply_markup=reply_markup)
        else:
            print('/'*88)
            Tg_Users.objects.create(user_id=message.chat.id, step=USER_STEP['ENTER_FIRST_NAME'])

            text = 'Salom Xush kelibsiz!!!\n\n'
            text += 'Ismingizni kiriting:'
            bot.send_message(message.chat.id, text)
    except Exception as e:
        print(e)


@bot.message_handler(regexp=BUTTONS['BACK'])
def back_message(message):
    print('/'*88)
    user = Tg_Users.objects.get(user_id=message.chat.id)
    if user.step == 3:
        start_message(message)
    else:
        user.step -= 2
        user.save()
        text_message(message)


@bot.message_handler(content_types=['text', 'contact'])
def text_message(message):
    switcher = {
        USER_STEP['ENTER_FIRST_NAME']: enter_first_name,
        USER_STEP['CHOOSE_LOCATION']: select_province,
        USER_STEP['SELECT_DISTRICT']: select_district,
        USER_STEP['NUMBER_OF_PASSANGERS']: number_of_passengers,
        USER_STEP['THANK_YOU_MESSAGE']: thank_you_message
    }
    print(Tg_Users.objects.get(user_id=message.chat.id).step)
    func = switcher.get(Tg_Users.objects.get(user_id=message.chat.id).step, lambda: start_message(message))
    func(message, bot)
