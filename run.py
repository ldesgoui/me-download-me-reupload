#!/usr/bin/env python3

import asyncio
import logging
import os
import re
import sys

import discord
import youtube_dl

# https://github.com/ytdl-org/youtube-dl/blob/ea89680aeae7c26af355ac23038e3a45f116649e/youtube_dl/extractor/twitch.py#L871
RE = re.compile(
    r"https?://(?:clips\.twitch\.tv/(?:embed\?.*?\bclip=|(?:[^/]+/)*)|(?:(?:www|go|m)\.)?twitch\.tv/[^/]+/clip/)\w+"
)
YTDL_OPTIONS = dict(format=os.getenv("YTDL_FORMAT", "360"), outtmpl="%(id)s.%(ext)s",)
TWITCH_CHANNEL = os.getenv("TWITCH_CHANNEL", "MOONMOON")
DISCORD_CHANNEL = int(os.getenv("DISCORD_CHANNEL", "193945356604538889"))

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(levelname)-8s %(module)s: %(message)s")
client = discord.Client()


@client.event
async def on_ready():
    logging.info(f"We have logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.id != DISCORD_CHANNEL:
        return

    matches = RE.finditer(message.content)
    urls = map(lambda match: match.group(0), matches)

    processed_urls = set()
    for url in urls:
        logging.info(f"Found clip URL: {url}")

        if url in processed_urls:
            logging.info("Skipping duplicate")
            continue
        processed_urls.add(url)

        info = await download(url, client.loop)
        filename = "{id}.{ext}".format_map(info)

        asyncio.create_task(delete(filename))

        if info["creator"] != TWITCH_CHANNEL:
            logging.info("Skipping clip not matching creator")
            continue

        with open(filename, "rb") as fp:
            logging.info(f"Uploading {filename}")
            await message.reply(
                "> {title}\nclipped by {uploader}".format_map(info),
                file=discord.File(fp),
            )


async def download(url, loop):
    with youtube_dl.YoutubeDL(YTDL_OPTIONS) as ytdl:
        return await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url)
        )


async def delete(filename):
    logging.info(f"Scheduled to delete {filename} in a minute")
    await asyncio.sleep(60)
    try:
        logging.info(f"Attempting to delete {filename}")
        os.remove(filename)
    except:
        logging.exception(f"Failed to delete {filename}")


if __name__ == "__main__":
    if "BOT_TOKEN" not in os.environ:
        logging.error(f"Must set environment variable BOT_TOKEN to your Discord bot token")
        sys.exit(1)
    logging.info(f"Reuploading clips from {TWITCH_CHANNEL} in channel {DISCORD_CHANNEL}")
    client.run(os.getenv("BOT_TOKEN"))
