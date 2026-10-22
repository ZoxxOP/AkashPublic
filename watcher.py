from pyrogram import filters
from pyrogram.types import Message

from __init__ import ananya
from call import Akash

welcome = 20
close = 30


@ananya.on_message(filters.video_chat_started, group=welcome)
@ananya.on_message(filters.video_chat_ended, group=close)
async def welcome(_, message: Message):
    await Akash.stop_stream_force(message.chat.id)
