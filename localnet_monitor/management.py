import argparse

from localnet_monitor.monitor import Monitor


class Management(object):
    def __init__(self):
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument('--config', default='config.yaml')
        args = parser.parse_args()
        Monitor(args.config).start()
