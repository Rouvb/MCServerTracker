# MCServerTracker
## Description
Collects Minecraft server data and sends the peak and average online player counts to a Discord webhook.
## Setup
Before running this program, please configure the config.json file.
## Installation (Virtual Environment)
### Linux
```
python3 -m venv venv_name
source venv_name/bin/activate
```
### Windows
```
py -m venv venv_name
call venv_name/Scripts/activate
```
## Installation (Docker)
```
docker build . -t <image_name>
docker run -it <image_name>
```