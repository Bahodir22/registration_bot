import datetime
from config import API_TOKEN, ADMIN_ID
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State


bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

class Form(StatesGroup):
    name = State()
    birth_date = State()
    adress = State()
    phone_number = State()


def valid_date(date_text: str):
    try:
        datetime.datetime.strptime(date_text, '%d.%m.%Y')
        return True
    except ValueError:
        return False



@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await message.answer(
        text=f"Assalomu alaykum {message.from_user.get_mention(as_html=True)} \nMen reguztelecom_bot!\nmijozlarni qo'llab-quvvatlash botiga xush kelibsiz!",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="🛠 xizmatlar haqida ma'lumot")],
                [types.KeyboardButton(text="🛍 Tariflar haqida ma'lumot")],
                [types.KeyboardButton(text="📝 ariza qoldirish")],
            ],
            resize_keyboard=True
        )
    )

    
    
@dp.message_handler(text="🛠 xizmatlar haqida ma'lumot")
async def cmd_menu1(message: types.Message):
    await message.answer(
        text=f"1084 - internet va IPTV xizmatlari"
              "\n1086 - telefon ta'mirlash byurosi"
              "\n1099 - mobil aloqa xizmatlari"
              "\n1155 - korporativ mijozlar uchun"

    )

@dp.message_handler(text="🛍 Tariflar haqida ma'lumot")
async def cmd_menu2(message: types.Message):
    await message.answer_photo(open("./images/phototariflar.jpg"))
    await message.answer(
        text=f"🔴 YANGI 1 - 109990 sum 20Mb/s"
            "\n🟡 YANGI 2 - 139990 sum 40Mb/s"
            "\n🟢 YANGI 3 - 169990 sum 60Mb/s"
            "\n🔵 YANGI 4 - 199990 sum 100Mb/s"

    )

@dp.message_handler(text="📝 ariza qoldirish")
async def cmd_menu3(message: types.Message):
    await message.answer(f"To'liq ism-familyangizni kiriting")
    await Form.name.set()


@dp.message_handler(state=Form.name)
async def form_name(message: types.Message, state: FSMContext = None) -> None:
    await state.update_data(
        {"full_name": message.text}
    )
    
    await message.answer(
        "Tug'ilgan kun oy yilingizni dd.mm.yyyy formatda kiriting.\n"
        "Masalan 31.12.1999"
    )
    
    await Form.next()
    
    
@dp.message_handler(state=Form.birth_date)
async def form_name(message: types.Message, state: FSMContext = None) -> None:
    if valid_date(message.text):
        # To'g'ri formatda kiritildi
        await state.update_data(
            {"birth_date": message.text}
        )
        
        await message.answer(
            "Yashash manzilingizni kiriting.\n"
            "Viloyat, mahalla, ko'cha, xonadon"
        )

        await Form.next()

    else:
        await message.answer(
            "Noto'g'ri format!\n"
            "Iltimos qayta tekshirib dd.mm.yyyy formatda kiriting.\n"
            "Masalan 31.12.1999"
        )
   

@dp.message_handler(state=Form.adress)
async def enter_adress(message: types.Message, state: FSMContext):

    await state.update_data(
        {"adress": message.text}
    )

    await message.answer(
        text="Pastdagi <b>«📞Telefon raqamni yuborish»</b> tugmasini bosib telefon raqamingizni jo'nating",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="📞Telefon raqamni yuborish", request_contact=True)]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )  
    )

    await Form.next()    



@dp.message_handler(content_types=types.ContentTypes.CONTACT, state=Form.phone_number)
async def enter_phone_number(message: types.Message, state: FSMContext):
    if message.contact.user_id == message.from_user.id:
        # o'zini kontakti
        phone_number = message.contact.phone_number 
        await state.update_data(
            {"phone_number": phone_number}
        )
        
        datas = await state.get_data()
        name = datas['full_name']
        birth_date = datas['birth_date']
        adress = datas['adress']
        phone_number = datas['phone_number']
        if phone_number[0] != '+':
            phone_number = '+' + phone_number
        txt = [
            f"👤Foydalanuvchi: {message.from_user.get_mention(as_html=True)}",
            f"👥Ismi: {name}",
            f"📆Tug'ilgan kuni: {birth_date}",
            f"📍Manzili: {adress}",
            f"📞Tel: {phone_number}"
        ]
        m = await message.answer(
            "\n".join(txt)
        )
        
        await bot.send_message(
            chat_id=ADMIN_ID,
            text="\n".join(txt),
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="✅Tasdiqlash", callback_data=f"ok_{message.from_user.id}")],
                [types.InlineKeyboardButton(text="❌Rad etish", callback_data=f"no_{message.from_user.id}")],
            ])
        )
        
        await m.reply("Sizning ma'lumotlaringiz adminga yuborildi. Tasdiqlanishini kuting.")
        
        await state.finish() 
    else:
        await message.answer(
            text="Iltimos faqat o'zingizning telefon raqamingizni yuboring.",
            reply_markup=types.ReplyKeyboardMarkup(
                keyboard=[
                    [types.KeyboardButton(text="📞Telefon raqamni yuborish", request_contact=True)]
                ],
                resize_keyboard=True,
                one_time_keyboard=True,
            )
        )
        

@dp.message_handler(content_types=types.ContentTypes.ANY, state=Form.phone_number)
async def enter_phone_number_error(message: types.Message, state: FSMContext):
    await message.answer(
        text="Iltimos faqat o'zingizning telefon raqamingizni yuboring.",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="📞Telefon raqamni yuborish", request_contact=True)]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
    )


@dp.callback_query_handler(text_startswith="ok_", user_id=ADMIN_ID)
async def admin_commit(call: types.CallbackQuery):
    await call.answer("✅Tasdiqlandi")
    await call.message.edit_text(
        text=call.message.text + "\n\n✅Tasdiqlandi",
    )
    user = call.data.replace("ok_", '')
    await bot.send_message(
        chat_id=user,
        text="Sizning ma'lumotlaringiz admin tomonidan tasdiqlandi. Endi botdan foydalanishingiz mumkin."
    )
    
    
@dp.callback_query_handler(text_startswith="no_", user_id=ADMIN_ID)
async def admin_cancel(call: types.CallbackQuery):
    await call.answer("❌Rad etildi")
    await call.message.edit_text(
        text=call.message.text + "\n\n❌Rad etildi",
    )
    user = call.data.replace("no_", '')
    await bot.send_message(
        chat_id=user,
        text="Sizning ma'lumotlaringiz admin tomonidan rad etildi😕"
    )


@dp.message_handler(commands="help")
async def help_handler(message : types.Message):
    await message.reply(f"1084 - internet va IPTV xizmatlari"
                        "\n1086 - telefon ta'mirlash byurosi"
                        "\n1099 - mobil aloqa xizmatlari"
                        "\n1155 - korporativ mijozlar uchun")
    
