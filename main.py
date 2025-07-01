import io
from datetime import datetime
import json
import logging
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen, Request

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from discord_webhook import DiscordWebhook, DiscordEmbed

from config import load_config

# Online player history data
online_history = {}

# Set up a basic logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def record_online_count(server_ip: str, online: int) -> None:
    # Append current online player count to online_history dict
    # online_history dict: {"server_ip": []}
    logger.info(f"Recording online count for {server_ip}...")
    global online_history
    if not online_history.get(server_ip):
        online_history[server_ip] = []
    online_history[server_ip].append({"online": online, "time": datetime.now()})
    online_values = [item["online"] for item in online_history[server_ip]]
    peak_online = max(online_values)
    logger.info(f"{server_ip} Online Count: {online} (Peak: {peak_online})")

def fetch_server_status(server_ip: str) -> None:
    # Get server data from mcsrvstat.us api
    # To do: add error handler
    logger.info(f"Fetching server data for {server_ip}...")
    url = f"https://api.mcsrvstat.us/3/{server_ip}"
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

    max_retries = 3
    retry_delay = 3

    for attempt in range(1, max_retries + 1):
        try:
            response = urlopen(request)
            json_data = json.load(response)
            current_online = json_data["players"]["online"]
            record_online_count(server_ip=server_ip, online=current_online)
            return

        except HTTPError as e:
            logger.warning(f"HTTP Error {e.code} from {url}: {e.reason}")
        except URLError as e:
            logger.warning(f"URL Error from {url}: {e.reason}")
        except KeyError as e:
            logger.warning(f"Missing key in JSON: {e}")
        except json.JSONDecodeError as e:
            logger.warning(f"JSON Decode Error: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error while processing {server_ip}: {e}")

        if attempt < max_retries:
            logger.info(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)

def send_webhook(server_ip: str) -> None:
    online_values = [item["online"] for item in online_history[server_ip]]
    average_online = int(sum(online_values) / len(online_values))
    peak_online = max(online_values)

    webhook_url = load_config()["webhook_url"]
    webhook = DiscordWebhook(url=webhook_url, username="Server Tracker")

    buf = visualize_data(server_ip=server_ip)
    webhook.add_file(file=buf, filename=f"{server_ip}.png")
    description = (
        f"> IP: `{server_ip}`\n"
        f"> Average Online: `{average_online}`\n"
        f"> Peak Online: `{peak_online}`\n"
    )

    embed = DiscordEmbed(title="Server Tracker", description=description, color=0x000000)
    embed.set_image(url=f"attachment://{server_ip}.png")
    embed.set_footer(text=f"{server_ip}")
    embed.set_timestamp()

    webhook.add_embed(embed)

    try:
        webhook.execute()
    except Exception as e:
        logger.warning(f"Unexpected error while processing {server_ip}: {e}")
    finally:
        buf.close()

def visualize_data(server_ip: str) -> io:
    times = [item["time"] for item in online_history[server_ip]]
    online_users = [item["online"] for item in online_history[server_ip]]

    if len(times) > 48:
        sample_rate = len(times) // 48
        times_sampled = times[::sample_rate]
        online_users_sampled = online_users[::sample_rate]
    else:
        times_sampled = times
        online_users_sampled = online_users

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(times_sampled, online_users_sampled, linewidth=2, color='red')
    ax.fill_between(times_sampled, online_users_sampled, color='red', alpha=0.25)

    ax.set_title(f"{server_ip}")
    ax.set_xlabel("Hour")
    ax.set_ylabel("Online Count")
    ax.grid(True)

    ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))
    plt.xticks(rotation=45)

    plt.margins(0)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()
    return buf

def clear_online_history() -> None:
    global online_history
    online_history = {}

def start_tracking_loop() -> None:
    tracking_time = load_config()["tracking_time"]
    server_ips = load_config()["server_ips"]
    while True:
        for server_ip in server_ips:
            fetch_server_status(server_ip)
        time.sleep(tracking_time)

def daily_report_loop() -> None:
    while True:
        logger.info("Checking if it's time to send report...")
        current_time = datetime.now()
        if current_time.hour == 0 and current_time.minute == 0:
            logger.info("Sending daily server report...")
            server_ips = load_config()["server_ips"]
            for server_ip in server_ips:
                send_webhook(server_ip=server_ip)
            clear_online_history()
        time.sleep(60)

def main() -> None:
    server_task = threading.Thread(target=start_tracking_loop)
    server_task.start()

    report_task = threading.Thread(target=daily_report_loop)
    report_task.start()

if __name__ == "__main__":
    main()