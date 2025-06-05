import datetime
import json
import logging
import threading
import time
from urllib.request import urlopen, Request

from discord_webhook import DiscordWebhook, DiscordEmbed

from config import load_config

# Config
online_count = {}

# Set up a basic logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def update_online_count(server_ip: str, online: int) -> None:
    # Append current online count to online_count dict
    # online_count dict: {"server_ip": []}
    logger.info(f"Updating Online Count for {server_ip}...")
    global online_count
    if not online_count.get(server_ip):
        online_count[server_ip] = []
    online_count[server_ip].append(online)
    peak_online = sorted(online_count[server_ip], reverse=True)[0]
    logger.info(f"{server_ip} Online Count: {online} (Peak: {peak_online})")

def get_server_data(server_ip: str) -> None:
    # Get server data from mcsrvstat.us api
    logger.info(f"Getting Server Data for {server_ip}...")
    url = f"https://api.mcsrvstat.us/3/{server_ip}"
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urlopen(request)
    json_data = json.load(html)
    current_online = json_data["players"]["online"]
    update_online_count(server_ip=server_ip, online=current_online)

def send_webhook(server_ip: str) -> None:
    average_online = int(sum(online_count[server_ip]) / len(online_count[server_ip]))
    peak_online = sorted(online_count[server_ip], reverse=True)[0]

    webhook_url = load_config()["webhook_url"]
    webhook = DiscordWebhook(url=webhook_url, username="Server Tracker")

    description = (
        f"> Average Online: {average_online}\n"
        f"> Peak Online: {peak_online}\n"
    )
    embed = DiscordEmbed(title="Server Tracker", description=description, color=0x000000)
    embed.set_footer(text=f"{server_ip}")

    webhook.add_embed(embed)
    webhook.execute()

def reset_online_count() -> None:
    global online_count
    online_count = {}

def server_data_task() -> None:
    tracking_time = load_config()["tracking_time"]
    server_ips = load_config()["server_ips"]
    while True:
        for server_ip in server_ips:
            get_server_data(server_ip)
        time.sleep(tracking_time)

def webhook_task() -> None:
    while True:
        current_time = datetime.datetime.now()
        if current_time.hour == 00 and current_time.minute == 00:
            server_ips = load_config()["server_ips"]
            for server_ip in server_ips:
                send_webhook(server_ip=server_ip)
            reset_online_count()
        time.sleep(60)

def main() -> None:
    server_task = threading.Thread(target=server_data_task())
    server_task.start()
    send_repost_task = threading.Thread(target=webhook_task())
    send_repost_task.start()

if __name__ == "__main__":
    main()