import telebot


class Telegram(object):
    def __init__(self, config, monitor):
        self.config = config
        self.monitor = monitor
        self.bot = telebot.TeleBot(self.config['token'])

    def send_alert(self, device, status=True):
        status = b'\xe2\x9c\x85' if status else b'\xE2\x9D\x8C'
        body = '%(status)s {name} ({mac}) {ip}'.format(**device)
        body = body.encode('utf-8')
        body = body % {b'status': status}
        self.bot.send_message(self.config['userid'], body)
