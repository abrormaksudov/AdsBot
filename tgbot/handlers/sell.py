import operator
from typing import Union, Dict, Any

import phonenumbers
from aiogram import types
from aiogram.utils.markdown import hunderline, hbold, hcode, hitalic
from aiogram_dialog import Dialog, Window, DialogManager, StartMode, ShowMode
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import Group, Row, Button, SwitchTo, \
    Start, Checkbox, Radio
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.when import Whenable

from tgbot.misc.states import Sell, Main


def get_active_section(state: str):
    sections = {
        'title': 'Заголовок',
        'description': 'Описание',
        'price': 'Цена',
        'contact': 'Контакты',
        'photo': 'Картинка',
        'tags': 'Теги'
    }
    return sections.get(state)


def make_tags(tag: str, where: str) -> str:
    tags = {
        "sell": "#продам",
        "buy": "#куплю",
        "extra": tag and "#" + tag
    }
    if tag:
        return f"{tags.get(where)}, {tags.get('extra')}"
    else:
        return tags.get(where)


def humanize_phone_number(phone_number: str):
    if not phone_number.startswith('+'):
        phone_number = '+' + phone_number
    phone_number = phonenumbers.parse(phone_number)
    return phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)


async def get_sell_text(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.current_context().widget_data
    print(data)
    state = dialog_manager.current_context().state.state.split(":")[-1]

    # entered data from user
    title: str = data.get('title') or '➖'
    description: str = data.get('description') or '➖'
    price = (data.get('price') and ((float(data.get('price')).is_integer() and int(data.get('price'))) or float(data.get('price')))) or '➖'
    currency = data.get('currency', '₴')
    negotiable = '(торг уместен)' if data.get('negotiable') else '(цена окончательна)'
    contact = data.get('contact') and humanize_phone_number(data.get('contact')) or '➖'
    photo = data.get('photos_file_id') and str(len(
        data.get('photos_file_id')
    )) + ' шт' or '➖'
    tags: str = make_tags(tag=data.get('tag'), where="sell")

    # identifying the active section
    ttitle = state == 'title' and hunderline('Заголовок товара или услуг') or 'Заголовок товара или услуг'
    tdescription = state == 'description' and hunderline('Описание товара или услуг') or 'Описание товара или услуг'
    tprice = state == 'price' and hunderline('Цена') or 'Цена'
    tcontact = state == 'contact' and hunderline('Контактные данные') or 'Контактные данные'
    tphoto = state == 'photo' and hunderline('Фото (опционально)') or 'Фото (опционально)'
    ttags = state == 'tags' and hunderline('Теги') or 'Теги'

    text = (f"1. {ttitle}: {hbold(title)}\n"
            f"2. {tdescription}: {hitalic(description)}\n"
            f"3. {tprice}: {hcode(str(price) + ' ' + (data.get('price') and currency or ''))} {data.get('price') and negotiable or ''}\n"
            f"4. {tcontact}: {hcode(contact)}\n"
            f"5. {tphoto}: {photo}\n"
            f"6. {ttags}: {tags}\n")

    match state:
        case 'title':
            if not data.get('title'):
                text = '🔡 Придумайте, затем введите короткий и привлекающий внимание ' \
                       'заголовок вашего товара или услуг, ' \
                       'чтобы заинтересовать потенциальных покупателей:\n\n' + text
            else:
                text = '🔡 Чтобы изменить заголовок товара или услуг, просто отправьте' \
                       'новое название.\n\n' + text

        case 'description':
            if not data.get('description'):
                text = '📝 Введите описание вашего товара или услуг. Пишите понятно и ' \
                       'будьте честны. Так вы избежите повторяющихся ' \
                       'вопросов. Добавьте деталей. Так покупателям будет проще ' \
                       'найти ваше объявление:\n\n' + text
            else:
                text = '📝 Чтобы изменить описание товара или услуг, просто отправьте' \
                       'новое описание.\n\n' + text

        case 'price':
            if not data.get('price'):
                text = '💸 Введите цену товара или услуг, так же укажите ' \
                       'валюту и уместен ли торг:\n\n' + text
            else:
                text = '💸 Чтобы изменить цену товара или услуг, просто отправьте ' \
                       'новую цену.\n\n' + text

        case 'contact':
            if not data.get('contact'):
                text = '📞 Введите номер телефона который будет отображаться в объявлении' \
                       ' или нажмите на кнопку ' \
                       '\"Отправить контакт\":\n\n' + text
            else:
                text = '📞 Чтобы изменить номер телефона, просто отправьте' \
                       'отправьте новый номер.\n\n' + text

        case 'photo':
            if not data.get('quantity'):
                text = '🖼 Отправьте картинки товара или услуг по одному ' \
                       '(этот раздел можно пропустить).\n' \
                       'P.s. Максимальное количество картинок: <code>5</code>:\n\n' + text
            else:
                text = '🖼 Чтобы изменить картинку товара или услуг, просто отправьте' \
                       'новую картинку, а чтобы удалить картинку нажми на ' \
                       'кнопку ниже.\n\n' + text

        case _:
            if not data.get('tag'):
                text = '#️⃣  Выберите тег своего товара или услуг нажав по кнопке ' \
                       'ниже:\n\n' + text
            else:
                text = '#️⃣  Чтобы изменить тег товара или услуг, сначала удалите текущий ' \
                       'тег, затем установите новый.\n\n' + text

    return {"sell_text": text, "page": get_active_section(state)}


async def change_page(_obj: Union[types.CallbackQuery, types.Message], button: Union[Button, TextInput],
                      manager: DialogManager, *_text):
    action: str = button.widget_id
    current_state = manager.current_context().state.state.split(":")[-1]

    if action == 'left':
        if current_state == 'title':
            await manager.dialog().switch_to(Sell.tags)
        else:
            await manager.dialog().back()
    elif action == 'right':
        if current_state == 'tags':
            await manager.dialog().switch_to(Sell.title)
        else:
            await manager.dialog().next()
    elif current_state != 'tags':
        await manager.dialog().next()


async def add_tag(_call: types.CallbackQuery, button: Button, manager: DialogManager):
    tag = button.widget_id

    tags = {
        "childs_world": "детский_мир",
        "real_estate": "недвижимость",
        "transport": "транспорт",
        "work": "работа",
        "animals": "животные",
        "house_garden": "дом_и_сад",
        "electronics": "электроника",
        "services": "услуги",
        "fashion_style": "мода_и_стиль",
        "sport": "спорт",
    }

    manager.current_context().widget_data['tag'] = tags.get(tag)


async def currency_selected(call: types.CallbackQuery, widget: Any, manager: DialogManager, item_id: str):
    currencies = {'USD': '$', 'EUR': '€', 'RUB': '₽', 'UAH': '₴'}
    manager.current_context().widget_data['currency'] = currencies[item_id]


async def delete_tag(_call: types.CallbackQuery, _button: Button, manager: DialogManager):
    manager.current_context().widget_data.pop('tag', None)


def tag_is_empty(_data: Dict, _widget: Whenable, manager: DialogManager):
    return manager.current_context().widget_data.get('tag') is None


def tag_exist(_data: Dict, _widget: Whenable, manager: DialogManager):
    return manager.current_context().widget_data.get('tag') is not None


# Restrictions
def fixed_size_64(text: str):
    if len(text) > 128:
        raise ValueError


def fixed_size_1024(text: str):
    if len(text) > 1024:
        raise ValueError


def positive_float(number: str):
    # min price is 0.01
    number = float(number)
    if not (number > 0.01):
        raise ValueError


def validate_phone_number(phone_number: str):
    try:
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number
        phone_number = phonenumbers.parse(phone_number)

        # shallow check whether the phone number is invalid
        if phonenumbers.is_possible_number(phone_number):
            # deep check whether the phone number is invalid
            if not phonenumbers.is_valid_number(phone_number):
                raise ValueError
        else:
            raise ValueError

    except phonenumbers.NumberParseException:
        # the input is really gibberish
        raise ValueError


async def invalid_input(message: types.Message, _widget: TextInput, manager: DialogManager):
    state = manager.current_context().state
    manager.show_mode = ShowMode.EDIT
    match state:
        case Sell.title:
            await message.answer("Максимальная длина заголовка товара или услуг 64 символов."
                                 " Попробуйте еще раз.")
        case Sell.description:
            await message.answer("Максимальная длина описания товара или услуг 128 символов."
                                 " Попробуйте еще раз.")
        case Sell.price:
            await message.answer("Цена должна быть числом и быть больше 0.01. Попробуйте еще раз.")
        case Sell.contact:
            await message.answer("Вы ввели не валидный номер! Попробуйте еще раз.")


async def pic_validator(message: types.Message, _dialog: ManagedDialogAdapterProto, manager: DialogManager):
    match message.content_type:
        case types.ContentType.PHOTO:
            photo = message.photo[-1]
            widget_data = manager.current_context().widget_data.setdefault('photos_file_id', [])
            widget_data.append(photo.file_id)
        case _:
            await message.answer("Вы ввели не валидную картинку! Попробуйте еще раз.")


# Buttons and dialogs
async def set_default(_, dialog_manager: DialogManager):
    await dialog_manager.dialog().find('r_currency').set_checked(event="", item_id="UAH")


async def get_currency_data(**_kwargs):
    currencies = [
        ('$', 'USD'),
        ('€', 'EUR'),
        ('₽', 'RUB'),
        ('₴', 'UAH')
    ]
    return {'currencies': currencies}


def tag_buttons():
    buttons = Group(
        Button(text=Const("#️⃣Детский мир"), id="childs_world", on_click=add_tag),
        Button(text=Const("#️⃣Недвижимость"), id="real_estate", on_click=add_tag),
        Button(text=Const("#️⃣Транспорт"), id="transport", on_click=add_tag),
        Button(text=Const("#️⃣Работа"), id="work", on_click=add_tag),
        Button(text=Const("#️⃣Животные"), id="animals", on_click=add_tag),
        Button(text=Const("#️⃣Дом и сад"), id="house_garden", on_click=add_tag),
        Button(text=Const("#️⃣Электроника"), id="electronics", on_click=add_tag),
        Button(text=Const("#️⃣Услуги"), id="services", on_click=add_tag),
        Button(text=Const("#️⃣Мода и стиль"), id="fashion_style", on_click=add_tag),
        Button(text=Const("#️⃣Спорт"), id="sport", on_click=add_tag),
        width=2,
        when=tag_is_empty
    )

    return buttons


def get_widgets():
    buttons = (
        Format(text="{sell_text}", when="sell_text"),
        Row(
            Button(text=Const("<<"), id="left", on_click=change_page),
            Button(text=Format(text="{page}"), id="page"),
            Button(text=Const(">>"), id="right", on_click=change_page)
        ),
        Row(
            Start(text=Const("🔚 Назад"), id="back_to_main", state=Main.main,
                  mode=StartMode.RESET_STACK),
            SwitchTo(text=Const("👁 Предпросмотр"), id="preview", state=Sell.preview),
            SwitchTo(text=Const("Готово"), id="done", state=Sell.done)
        )
    )
    return buttons


sell_dialog = Dialog(
    Window(
        *get_widgets(),
        TextInput(
            id="title",
            type_factory=fixed_size_64,
            on_error=invalid_input,
            on_success=change_page),
        state=Sell.title,
        getter=[get_sell_text]
    ),
    Window(
        *get_widgets(),
        TextInput(
            id="description",
            type_factory=fixed_size_1024,
            on_error=invalid_input,
            on_success=change_page),
        state=Sell.description,
        getter=[get_sell_text]
    ),
    Window(
        Checkbox(
            checked_text=Const("Торг уместен: Да ✅"),
            unchecked_text=Const("Торг уместен: Нет ❌"),
            id="negotiable",
            default=False
        ),
        Radio(
            checked_text=Format("✔️ {item[0]}"),
            unchecked_text=Format("{item[0]}"),
            id="r_currency",
            item_id_getter=operator.itemgetter(1),
            items="currencies",
            on_click=currency_selected
        ),
        *get_widgets(),
        TextInput(
            id="price",
            type_factory=positive_float,
            on_error=invalid_input,
            on_success=change_page
        ),
        state=Sell.price,
        getter=[get_sell_text, get_currency_data]
    ),
    Window(
        *get_widgets(),
        TextInput(
            id="contact",
            type_factory=validate_phone_number,
            on_error=invalid_input,
            on_success=change_page
        ),
        state=Sell.contact,
        getter=[get_sell_text]
    ),
    Window(
        *get_widgets(),
        MessageInput(pic_validator, content_types=[types.ContentType.ANY]),
        state=Sell.photo,
        getter=[get_sell_text]
    ),
    Window(
        Button(
            text=Const("Удалить тег"),
            id="delete_tag",
            when=tag_exist,
            on_click=delete_tag
        ),
        tag_buttons(),
        *get_widgets(),
        state=Sell.tags,
        getter=[get_sell_text]
    ),
    Window(

        state=Sell.done,
        getter=[get_sell_text]
    ),
    on_start=set_default
)
