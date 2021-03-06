import os
import time
from bot import Config, CMD, LOGGER
from pyrogram import Client, filters
from bot.helpers.translations import lang
from bot.helpers.utils.storage_clean import clean_up
from bot.helpers.functions.file_upload import pyro_upload
from bot.helpers.database.database import check_user, checkUserSet
from bot.helpers.functions.display_progress import progress_for_pyrogram

@Client.on_message(filters.command(CMD.RENAME))
async def rename(bot, update):
    user_id = update.from_user.id
    await check_user(user_id)
    if update.chat.id in Config.AUTH_CHAT or user_id in Config.ADMINS:
        try:
            file = update.reply_to_message
        except:
            file = None
        try:
            new_name = update.text.split(" ", maxsplit=1)[1]
        except:
            return await bot.send_message(
                chat_id=update.chat.id,
                text=lang.ERR_USAGE,
                reply_to_message_id=update.message_id
            )
        if file:
            reply_to_id = update.reply_to_message.message_id
            new_name_path = f"{Config.DOWNLOAD_BASE_DIR}/{reply_to_id}/{new_name}"
            file_path = f"{Config.DOWNLOADS_FOLDER}/{reply_to_id}/"
            init_msg = await bot.send_message(
                chat_id=update.chat.id,
                text=lang.INIT_DOWNLOAD_FILE,
                reply_to_message_id=update.message_id
            )
            c_time = time.time()
            org_file_path = await bot.download_media(
                message=update.reply_to_message,
                file_name=file_path,
                progress=progress_for_pyrogram,
                progress_args=(
                    lang.INIT_DOWNLOAD_FILE,
                    init_msg,
                    c_time
                )
            )
            try:
                os.rename(org_file_path, new_name_path)
            except Exception as e:
                return await bot.send_message(
                    chat_id=update.chat.id,
                    text=e,
                    reply_to_message_id=update.message_id
                )
            video, photo = await checkUserSet(update.from_user.id)
            await pyro_upload(bot, update, new_name_path, new_name, video, photo, reply_to_id, init_msg)
            await bot.send_message(
                chat_id=update.chat.id,
                text=lang.UPLOAD_SUCCESS,
                reply_to_message_id=reply_to_id
            )
            await bot.delete_messages(
                chat_id=update.chat.id,
                message_ids=init_msg.message_id
            )
            await clean_up(file_path, reply_to_id)
        else:
            await bot.send_message(
                chat_id=update.chat.id,
                text=lang.ERR_USAGE,
                reply_to_message_id=update.message_id
            )
            
