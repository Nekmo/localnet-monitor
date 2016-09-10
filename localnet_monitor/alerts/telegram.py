import telebot


class Telegram(object):
    def __init__(self, config, monitor):
        self.config = config
        self.monitor = monitor
        self.bot = telebot.TeleBot(self.config['token'])

    def send_alert(self, device, status=True):
        self.bot.send_message(self.config['userid'], '{} {}'.format(device, status))
