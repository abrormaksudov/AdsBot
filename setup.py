from aiogram import Dispatcher
from aiogram_dialog import DialogRegistry

from tgbot.handlers.admin.admin_panel import admin_dialog
from tgbot.handlers.admin.show_user import show_user_dialog, register_show_product
from tgbot.handlers.buy_and_sell.dialogs import sell_dialog, buy_dialog, preview_dialog, confirm_dialog
from tgbot.handlers.edit_ad_status import register_ad_status_handler
from tgbot.handlers.edit_buy_and_sell.dialogs import edit_sell_ad_dialog, edit_buy_ad_dialog
from tgbot.handlers.edit_buy_and_sell.my_ads import my_ads_dialog
from tgbot.handlers.edit_buy_and_sell.show_my_ad import show_my_ad_dialog
from tgbot.handlers.group.post_reactions import register_post_reaction
from tgbot.handlers.main_handler import main_dialog
from tgbot.handlers.admin.search_user import register_inline_mode
from tgbot.handlers.start import register_start
from tgbot.handlers.test import register_test


def register_all_dialogs(dialog_registry: DialogRegistry):
    dialog_registry.register(main_dialog)

    dialog_registry.register(admin_dialog)
    dialog_registry.register(show_user_dialog)

    dialog_registry.register(sell_dialog)
    dialog_registry.register(buy_dialog)
    dialog_registry.register(preview_dialog)
    dialog_registry.register(confirm_dialog)

    dialog_registry.register(my_ads_dialog)
    dialog_registry.register(show_my_ad_dialog)
    dialog_registry.register(edit_sell_ad_dialog)
    dialog_registry.register(edit_buy_ad_dialog)


def register_all_handlers(dp: Dispatcher):
    register_post_reaction(dp)
    register_show_product(dp)
    register_start(dp)
    register_test(dp)
    register_ad_status_handler(dp)
    register_inline_mode(dp)
