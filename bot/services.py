from telebot.types import KeyboardButton
from telebot.types import ReplyKeyboardMarkup
from telebot.types import ReplyKeyboardRemove

from bot.models import Orders
from bot.models import Tg_Users

from bot.const import BUTTONS
from bot.const import USER_STEP
from bot.const import CHANNEL_ID

from data.models import Province
from data.models import District


def set_lang(message, bot):
    lan = ""
    if message.text == '🇺🇿 O\'zbek':
        lan = 'uz'
    if message.text == '🇷🇺 Руский':
        lan = 'rus'

    user_id = message.chat.id
    user = Tg_Users.objects.get(user_id=user_id)
    if not user.first_name:
        user.step = USER_STEP['ENTER_FIRST_NAME']
        user.lan = lan
        user.save()

        text = ''
        if user.lan == 'uz':
            text = 'Salom! Iltimos, ismingizni kiriting:\n\n'
        if user.lan == 'rus':
            text += 'Привет! Пожалуйста, введите ваше имя:'
        bot.send_message(user_id, text, reply_markup=ReplyKeyboardRemove())
    else:
        user.step = USER_STEP['ENTER_FIRST_NAME']
        user.lan = lan
        user.save()
        enter_first_name(message, bot)


def enter_first_name(message, bot):
    try:
        user = Tg_Users.objects.get(user_id=message.from_user.id)
        if not user.first_name:
            user.first_name = message.text
            
        Orders.objects.filter(user__user_id=user.user_id, status=False).delete()
            
        user.step = USER_STEP['CHOOSE_LOCATION']
        user.save()
        
        if user.lan == 'uz':
            text = 'Qayerdan murojat qilyapsiz?'
            provinces = Province.objects.all().values_list('name_uz', flat=True)
        if user.lan == 'rus':
            text = 'Откуда вы подаете заявление?'
            provinces = Province.objects.all().values_list('name_ru', flat=True)

        reply_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

        buttons = [KeyboardButton(text=text) for text in provinces]
        reply_markup.add(*buttons)

        bot.send_message(message.from_user.id, text, reply_markup=reply_markup)
    except Exception as e:
        print(e)



def select_province(message, bot):
    try:
        user = Tg_Users.objects.get(user_id=message.from_user.id)

        if Orders.objects.filter(user=user, status=False, from_to__isnull=False).exists():
            order = Orders.objects.get(user=user, status=False, from_to__isnull=False)
            order.where = None
            order.save()
            if user.lan =='uz':
                selected_province_name = order.from_to
            else:
                selected_province_name = order.from_to.name_ru
        else:
            selected_province_name = message.text
        print(selected_province_name)
        if user.lan == 'uz':
            selected_province = Province.objects.get(name_uz=selected_province_name)
            districts = District.objects.exclude(province=selected_province)
        if user.lan == 'rus':
            selected_province = Province.objects.get(name_ru=selected_province_name)
            districts = District.objects.exclude(province=selected_province)

        if districts:
            reply_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            if user.lan == 'uz':
                buttons = [KeyboardButton(text=district.name_uz) for district in districts]
                reply_keyboard.add(*buttons)
                reply_keyboard.add(KeyboardButton(text=BUTTONS['BACK_UZ']))
            if user.lan == 'rus':
                buttons = [KeyboardButton(text=district.name_ru) for district in districts]
                reply_keyboard.add(*buttons)
                reply_keyboard.add(KeyboardButton(text=BUTTONS['BACK_RU']))

            Tg_Users.objects.filter(user_id=message.from_user.id).update(step=USER_STEP['SELECT_DISTRICT'])

            if not Orders.objects.filter(user=user, status=False, from_to__isnull=False).exists():
                print(selected_province.name_ru)
                Orders.objects.create(user=user, from_to=selected_province, status=False)

            if user.lan == 'uz':
                text = f"Iltimos {selected_province_name}dan, tumanni tanlang :"
            if user.lan == 'rus':
                text = f"Пожалуйста, выберите район из {selected_province_name}:"

            bot.send_message(message.from_user.id, text, reply_markup=reply_keyboard)
        else:
            text = 'Sorry, there are no districts available for this province.'
            bot.send_message(message.from_user.id, text)
    except Exception as e:
        text = 'Sorry, there are no districts available for this province.'
        bot.send_message(message.from_user.id, text)
        print(e)


def select_district(message, bot):
    try:
        user = Tg_Users.objects.get(user_id=message.from_user.id)
        if not Orders.objects.filter(user=user, status=False, where__isnull=False).exists():
            if user.lan == 'uz':
                selected_d = District.objects.get(name_uz=message.text)
            if user.lan == 'rus':
                selected_d = District.objects.get(name_ru=message.text)

            order = Orders.objects.get(user=user, status=False)
            order.where = selected_d
            order.save()

        reply_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        if user.lan == 'uz':
            buttons = [KeyboardButton(text=str(num)) for num in range(1, 5)]
            reply_markup.add(*buttons)
            reply_markup.add(KeyboardButton(text=BUTTONS['BACK_UZ']))
        if user.lan == 'rus':
            buttons = [KeyboardButton(text=str(num)) for num in range(1, 5)]
            reply_markup.add(*buttons)
            reply_markup.add(KeyboardButton(text=BUTTONS['BACK_RU']))

        Tg_Users.objects.filter(user_id=message.from_user.id).update(step=USER_STEP['NUMBER_OF_PASSANGERS'])
        if user.lan == 'uz':
            text = "Odam soni:"
        if user.lan == 'rus':
            text = "Число людей:"
        bot.send_message(message.from_user.id, text, reply_markup=reply_markup)
    except Exception as e:
        text = 'Sorry, there are no districts available for this province.'
        bot.send_message(message.from_user.id, text)
        print(e)


def number_of_passengers(message, bot):
    try:
        if int(message.text) <= 4:
            user = Tg_Users.objects.get(user_id=message.from_user.id)
            order = Orders.objects.get(user=user, status=False)
            order.seats = int(message.text)
            order.save()
            if user.lan == 'uz':
                buttons = KeyboardButton(text="Raqamni jo'natish", request_contact=True)
                reply_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                reply_markup.add(buttons)
                reply_markup.add(KeyboardButton(text=BUTTONS['BACK_UZ']))
            if user.lan == 'rus':
                buttons = KeyboardButton(text="Отправить номер", request_contact=True)
                reply_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                reply_markup.add(buttons)
                reply_markup.add(KeyboardButton(text=BUTTONS['BACK_RU']))

            if user.lan == 'uz':
                text = '"Raqamni jo\'natish" tugmasi orqali raqamingzni jo\'nating'
            if user.lan == 'rus':
                text = " Отправьте свой номер с помощью кнопки «Отправить номер»"

            bot.send_message(message.from_user.id, text, reply_markup=reply_markup)

            Tg_Users.objects.filter(user_id=message.from_user.id).update(step=USER_STEP['THANK_YOU_MESSAGE'])
        else:
            user = Tg_Users.objects.get(user_id=message.from_user.id)
            reply_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            if user.lan == 'uz':
                buttons = [KeyboardButton(text=str(num)) for num in range(1, 5)]
                reply_markup.add(*buttons)
                reply_markup.add(KeyboardButton(text=BUTTONS['BACK_UZ']))
            if user.lan == 'rus':
                buttons = [KeyboardButton(text=str(num)) for num in range(1, 5)]
                reply_markup.add(*buttons)
                reply_markup.add(KeyboardButton(text=BUTTONS['BACK_RU']))

            bot.send_message(message.from_user.id, "Fuck You Bitch", reply_markup=reply_markup)
    except Exception as e:
        user = Tg_Users.objects.get(user_id=message.from_user.id)
        reply_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        if user.lan == 'uz':
            buttons = [KeyboardButton(text=str(num)) for num in range(1, 5)]
            reply_markup.add(*buttons)
            reply_markup.add(KeyboardButton(text=BUTTONS['BACK_UZ']))
        if user.lan == 'rus':
            buttons = [KeyboardButton(text=str(num)) for num in range(1, 5)]
            reply_markup.add(*buttons)
            reply_markup.add(KeyboardButton(text=BUTTONS['BACK_RU']))

        bot.send_message(message.from_user.id, "Fuck You Bitch", reply_markup=reply_markup)




def thank_you_message(message, bot):
    Tg_Users.objects.filter(user_id=message.chat.id).update(step=2)
    user = Tg_Users.objects.get(user_id=message.from_user.id)
    if user.lan == 'uz':
        text = "Rahmat tez orada siz bn bog'lanamiz!"
        province = Province.objects.all().values_list('name_uz', flat=True)
    if user.lan == 'rus':
        text = "Спасибо, и мы свяжемся с вами в ближайшее время!"
        province = Province.objects.all().values_list('name_ru', flat=True)

    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [KeyboardButton(text=text) for text in province]
    reply_markup.add(*buttons)
    bot.send_message(message.chat.id, text, reply_markup=reply_markup)

    user = Tg_Users.objects.get(user_id=message.chat.id)
    order = Orders.objects.get(user=user, status=False)
    order.status = True
    order.save()
    user_name = message.chat.first_name
    user_from = message.chat.username
    from_to = order.from_to
    where = order.where
    seats = order.seats
    user_contact = message.contact.phone_number

    channel_text = (
        f"New user contact:\n"
        f"Name: {user_name}\n"
        f"From: {user_from}\n"
        f"Contact: {user_contact}\n"
        f"Pickup Location: {from_to}\n"
        f"Drop-off Location: {where}\n"
        f"Number of Seats: {seats}"
    )

    bot.send_message(CHANNEL_ID, channel_text)
