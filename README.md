# JamminizBot

JamminizBot is a Discord bot designed for scheduling and managing events for online gaming groups.

## Installation

1. Clone the repository:

```
git clone https://github.com/NaLDo627/jamminizbot.git
cd jamminizbot
```


2. Install the required packages:

```
pip install -r requirements.txt
```


3. Set the following environment variables:

- `DISCORD_BOT_TOKEN`: token for Discord
- `DOCKER_PASSWORD`: password of Docker Hub
- `DOCKER_USERNAME`: username of Docker Hub
- `PAPAGO_CLIENT_ID`: client ID issued by Naver development center
- `PAPAGO_CLIENT_SECRET`: client secret issued by Naver development center
- `SSH_HOST`: SSH host of server to deploy application
- `SSH_PORT`: SSH port of server to deploy application
- `SSH_PRIVATE_KEY`: SSH private key of server to deploy application
- `SSH_USERNAME`: SSH username of server to deploy application

4. Start the bot:

```
python main.py
```


## Deployment

To deploy the bot, follow these steps:

1. Clone the repository on the remote server:

```
git clone https://github.com/NaLDo627/jamminizbot.git
cd jamminizbot
```

2. Copy the `docker-compose.yml` file to the remote server:

```
scp docker-compose.yml [username]@[server]:~/jamminizbot/
```


3. SSH into the remote server:

```
ssh [username]@[server]
```


4. Navigate to the bot's directory and start the container:

```
cd jamminizbot
docker-compose pull
docker-compose up -d
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for more information.
