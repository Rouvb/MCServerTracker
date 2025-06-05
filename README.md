# MCServerTracker
A lightweight Python tool that monitors Minecraft server player activity and sends **average** and **peak online player counts** to a Discord webhook daily.
## 📌 Features
- ⛏️ Tracks real-time player data from Minecraft servers
- 📊 Aggregates average and peak player counts
- 📤 Sends daily summary via Discord webhook
- 🔁 Customizable tracking interval
- 🐳 Docker support for easy deployment
## ⚙ Configuration
Create and edit `config.json` in the root directory.
```json
{
  "server_ips": ["mc.example.com", "123.45.67.89"],
  "webhook_url": "https://discord.com/api/webhooks/...",
  "tracking_time": 300  // seconds between checks
}
```
## 🚀 Installation (Virtual Environment)
### Using Virtual Environment
#### Linux / macOS
```
python3 -m venv venv_name
source venv_name/bin/activate
pip install -r requirements.txt
python main.py
```
#### Windows
```
py -m venv venv_name
call venv_name/Scripts/activate
pip install -r requirements.txt
python main.py
```
## 🐳 Using Docker
```
docker build . -t <image_name>
docker run -it <image_name>
```
## 👥 Credits
[**ChatGPT**](https://chatgpt.com/) - Naming Conventions and README.md Format Guidelines