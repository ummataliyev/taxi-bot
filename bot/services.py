from telebot.types import KeyboardButton
from telebot.types import ReplyKeyboardMarkup


from bot.models import Tg_Users
from bot.const import USER_STEP
from bot.const import BUTTONS


from data.models import Province
from data.models import District


def enter_first_name(message, bot):
    Tg_Users.objects.filter(user_id=message.from_user.id).update(first_name=message.text, step=USER_STEP['CHOOSE_LOCATION'])
    text = 'Nima buyurtma beramiz ?'
    category_qs = Province.objects.all().values_list('name', flat=True)
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    buttons = [KeyboardButton(text=text) for text in category_qs]
    reply_markup.add(*buttons)

    bot.send_message(message.from_user.id, text, reply_markup=reply_markup)


def select_district(message, bot):
    try:
        selected_province_name = message.text
        selected_province = Province.objects.get(name=selected_province_name)
        # print(selected_province)
        districts = District.objects.exclude(province=selected_province)
        
        if districts:
            reply_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

            buttons = [KeyboardButton(text=district.name) for district in districts]
            print(buttons)
            reply_keyboard.add(*buttons)

            Tg_Users.objects.filter(user_id=message.from_user.id).update(step=USER_STEP['SELECT_DISTRICT'])
            text = f"Please select a district from {selected_province_name}:"
            bot.send_message(message.from_user.id, text, reply_markup=reply_keyboard)
        else:
            text = 'Sorry, there are no districts available for this province.'
            bot.send_message(message.from_user.id, text)

    except Exception as e:
        print(e)
