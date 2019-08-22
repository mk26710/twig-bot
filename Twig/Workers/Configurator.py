import json
import time

with open('./config/master.json', encoding='utf-8') as f:
    config = json.load(f)

BOT_MAINTAINERS = config['MAINTAINERS']
BOT_PREFIX = config['PREFIX']
BOT_XP_LOGS = config['XP_LOG_CHANNEL_ID']
BOT_MAIN_LOGS = config['LOG_CHANNEL_ID']
BOT_PLAYING_GAME_NAME = config['STATUS']
BOT_STARTED_AT = time.time()
start_time = BOT_STARTED_AT
is_no_perm_notifications_enabled = config['SHOW_NO_PERMS_MESSAGES']

f.close()