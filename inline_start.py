import random

from pyrogram.enums import ButtonStyle
from pyrogram.types import InlineKeyboardButton

import config
from __init__ import ananya


def random_style():
    return random.choice(
        [
            ButtonStyle.PRIMARY,
            ButtonStyle.SUCCESS,
            ButtonStyle.DANGER,
        ]
    )


def start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_1"],
                url=f"https://t.me/{ananya.username}?startgroup=true",
                style=random_style(),
            ),
            InlineKeyboardButton(
                text=_["S_B_2"],
                url=config.SUPPORT_GROUP,
                style=random_style(),
            ),
        ],
    ]
    return buttons


def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{ananya.username}?startgroup=true",
                style=random_style(),
            )
        ],
        [
            InlineKeyboardButton(
                text=_["L_N_G"],
                callback_data="LG",
                style=random_style(),
            ),
            InlineKeyboardButton(
                text=_["S_B_5"],
                user_id=config.OWNER_ID,
                style=random_style(),
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["S_B_6"],
                url=config.SUPPORT_CHANNEL,
                style=random_style(),
            ),
            InlineKeyboardButton(
                text=_["S_B_9"],
                url=config.SUPPORT_GROUP,
                style=random_style(),
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["S_B_4"],
                callback_data="help_page_1",
                style=random_style(),
            ),
        ],
    ]
    return buttons


def about_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_6"],
                url=config.SUPPORT_CHANNEL,
                style=random_style(),
            ),
            InlineKeyboardButton(
                text=_["S_B_2"],
                url=config.SUPPORT_GROUP,
                style=random_style(),
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["BACK_BUTTON"],
                callback_data="settingsback_helper",
                style=random_style(),
            )
        ],
    ]
    return buttons


def owner_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_H_1"],
                url=config.INSTAGRAM,
                style=random_style(),
            ),
            InlineKeyboardButton(
                text=_["S_H_2"],
                url=config.YOUTUBE,
                style=random_style(),
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["S_H_3"],
                url=config.GITHUB,
                style=random_style(),
            ),
            InlineKeyboardButton(
                text=_["S_H_4"],
                url=config.DONATE,
                style=random_style(),
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["BACK_BUTTON"],
                callback_data="settingsback_helper",
                style=random_style(),
            )
        ],
    ]
    return buttons
