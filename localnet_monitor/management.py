from localnet_monitor.monitor import Monitor


class Management(object):
    def __init__(self):
        Monitor('config.yaml').start()
