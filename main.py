import asyncio
import importlib
from pyrogram import idle
from pyrogram.types import BotCommand
from pytgcalls.exceptions import NoActiveGroupCall
import config
from __init__ import LOGGER, ananya, userbot
from call import Akash
from misc import sudo
from plugins import ALL_MODULES
from database import get_banned_users, get_gbanned
from config import BANNED_USERS

COMMANDS = [
    BotCommand("start", "🚀 Start bot"),
    BotCommand("help", "❓ Help menu and Many More Management Commands"),
    BotCommand("ping", "📡 Ping and system stats"),
    BotCommand("play", "🎵 Start streaming the requested track"),
    BotCommand("vplay", "📹 Start video streaming"),
    BotCommand("playforce", "⚠️ Force play audio track"),
    BotCommand("vplayforce", "⚠️ Force play video track"),
    BotCommand("pause", "⏸ Pause the stream"),
    BotCommand("resume", "▶️ Resume the stream"),
    BotCommand("skip", "⏭ Skip the current track"),
    BotCommand("end", "🛑 End the stream"),
    BotCommand("stop", "🛑 Stop the stream"),
    BotCommand("queue", "📄 Show track queue"),
    BotCommand("auth", "➕ Add a user to auth list"),
    BotCommand("unauth", "➖ Remove a user from auth list"),
    BotCommand("authusers", "👥 Show list of auth users"),
    BotCommand("cplay", "📻 Channel audio play"),
    BotCommand("cvplay", "📺 Channel video play"),
    BotCommand("cplayforce", "🚨 Channel force audio play"),
    BotCommand("cvplayforce", "🚨 Channel force video play"),
    BotCommand("channelplay", "🔗 Connect group to channel"),
    BotCommand("loop", "🔁 Enable/disable loop"),
    BotCommand("stats", "📊 Bot stats"),
    BotCommand("shuffle", "🔀 Shuffle the queue"),
    BotCommand("seek", "⏩ Seek forward"),
    BotCommand("seekback", "⏪ Seek backward"),
    BotCommand("song", "🎶 Download song (mp3/mp4)"),
    BotCommand("speed", "⏩ Adjust audio playback speed (group)"),
    BotCommand("cspeed", "⏩ Adjust audio speed (channel)"),
]


async def setup_bot_commands():
    """Setup bot commands during startup"""
    try:
        await ananya.set_bot_commands(COMMANDS)
        LOGGER("AnanyaMusic").info("Bot commands set successfully!")
        
    except Exception as e:
        LOGGER("AnanyaMusic").error(f"Failed to set bot commands: {str(e)}")

async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("Assistant client variables not defined, exiting...")
        exit()

    await sudo()

    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass

    await ananya.start()
    
    await setup_bot_commands()

    for all_module in ALL_MODULES:
        importlib.import_module(all_module)

    LOGGER("AnanyaMusic.plugins").info("Successfully Imported Modules...")

    await userbot.start()
    await Akash.start()

    try:
        await Akash.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("AnanyaMusic").error(
            "Please turn on the videochat of your log group/channel.\n\nStopping Bot..."
        )
        exit()
    except:
        pass

    await Akash.decorators()

    LOGGER("AnanyaMusic").info(
        "\x41\x6e\x61\x6e\x79\x61\x20\x4d\x75\x73\x69\x63\x20\x53\x74\x61\x72\x74\x65\x64\x20\x53\x75\x63\x63\x65\x73\x73\x66\x75\x6c\x6c\x79\x0a\x0a\x44\x6f\x6e\x27\x74\x20\x66\x6f\x72\x67\x65\x74\x20\x74\x6f\x20\x76\x69\x73\x69\x74\x20\x40\x54\x65\x61\x6d\x41\x6e\x61\x6e\x79\x61\x42\x6f\x74\x73"
    )

    await idle()

    await ananya.stop()
    await userbot.stop()
    LOGGER("AnanyaMusic").info("Stopping Ananya Music Bot...🥺")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
