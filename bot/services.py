from telebot.types import KeyboardButton
from telebot.types import ReplyKeyboardMarkup

from bot.models import Tg_Users, Orders
from bot.const import USER_STEP
from bot.const import BUTTONS

from data.models import Province
from data.models import District


def enter_first_name(message, bot):
    Tg_Users.objects.filter(user_id=message.from_user.id).update(first_name=message.text, step=USER_STEP['CHOOSE_LOCATION'])
    text = 'Qayerdan murojat qilyapsiz ?'
    provinces = Province.objects.all().values_list('name', flat=True)
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    buttons = [KeyboardButton(text=text) for text in provinces]
    reply_markup.add(*buttons)

    bot.send_message(message.from_user.id, text, reply_markup=reply_markup)


def select_province(message, bot):
    try:
        user = Tg_Users.objects.get(user_id=message.from_user.id)
        if Orders.objects.filter(user=user, status=False, from_to__isnull=False).exists():
            selected_province_name = Orders.objects.get(user=user, status=False, from_to__isnull=False).from_to
        else:
            selected_province_name = message.text
        selected_province = Province.objects.get(name=selected_province_name)
        districts = District.objects.exclude(province=selected_province)

        if districts:
            reply_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

            buttons = [KeyboardButton(text=district.name) for district in districts]
            print(buttons)
            reply_keyboard.add(*buttons)
            reply_keyboard.add(KeyboardButton(text=BUTTONS['BACK']))

            Tg_Users.objects.filter(user_id=message.from_user.id).update(step=USER_STEP['SELECT_DISTRICT'])
            if not Orders.objects.filter(user=user, status=False, from_to__isnull=False).exists():
                Orders.objects.create(user=user, from_to=selected_province, status=False)
                
            text = f"Please select a district from {selected_province_name}:"
            bot.send_message(message.from_user.id, text, reply_markup=reply_keyboard)
            
        else:
            text = 'Sorry, there are no districts available for this province.'
            bot.send_message(message.from_user.id, text)

    except Exception as e:
        print(e)


def select_district(message, bot):
    try:
        user = Tg_Users.objects.get(user_id=message.from_user.id)
        if not Orders.objects.filter(user=user, status=False, where__isnull=False).exists():
            print(message.text)
            selected_d = District.objects.get(name=message.text)
            order = Orders.objects.get(user=user, status=False)
            order.where=selected_d
            order.save()
        else:
            order = Orders.objects.get(user=user, status=False)
            order.where = None
            order.save()
        reply_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

        buttons = [KeyboardButton(text=str(num)) for num in range(1, 5)]
        reply_markup.add(*buttons)
        reply_markup.add(KeyboardButton(text=BUTTONS['BACK']))

        Tg_Users.objects.filter(user_id=message.from_user.id).update(step=USER_STEP['NUMBER_OF_PASSANGERS'])
        text = "Odam soni:"
        bot.send_message(message.from_user.id, text, reply_markup=reply_markup)

    except Exception as e:
        print(e)


def number_of_passengers(message, bot):
    try:
        reply_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = KeyboardButton(text="Raqamni jo'natish", request_contact=True)
        reply_markup.add(buttons)
        text = " Raqamni jo'natish tugmasi orqali raqamingzni jo'nating"
        bot.send_message(message.from_user.id, text, reply_markup=reply_markup)

        Tg_Users.objects.filter(user_id=message.from_user.id).update(step=USER_STEP['THANK_YOU_MESSAGE'])

    except Exception as e:
        print(e)


def thank_you_message(message, bot):
    print(message.contact.phone_number)
    Tg_Users.objects.filter(user_id=message.chat.id).update(step=2)

    text = "Rahmat tez orada siz bn bog'lanamiz!"

    province = Province.objects.all().values_list('name', flat=True)
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    buttons = [KeyboardButton(text=text) for text in province]
    reply_markup.add(*buttons)

    bot.send_message(message.chat.id, text, reply_markup=reply_markup)
