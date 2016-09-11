import importlib
from time import sleep

from localnet_monitor.config import Config
from localnet_monitor.scan import scan_networks


def substract_lists(list1, list2):
    return [a for a in list1 if a not in list2]


def import_class(name):
    components = name.split('.')
    mod = importlib.import_module('.'.join(components[:-1]))
    mod = getattr(mod, components[-1])
    return mod


class Monitor(object):
    def __init__(self, config_file):
        self.config = Config(config_file)
        self.devices = []
        self.blacklist = self.config.get('blacklist', {})
        self.whitelist = self.config.get('whitelist', {})
        self.devices_connected = []
        self.disconnect_count = {}
        self.alerts = self.get_alerts()

    def get_alerts(self):
        alerts = []
        for name, config in self.config.get('alerts', {}).items():
            mod_class = import_class("localnet_monitor.alerts.{}.{}".format(name, name.title()))
            alerts.append(mod_class(config, self))
        return alerts

    def set_device_params(self, device):
        mac = device['mac']
        # First try whitelist. After, blacklist. Otherwise params = {}
        params = self.whitelist.get(mac, self.blacklist.get(mac, {}))
        device.update(params)

    def set_devices_params(self, devices):
        for device in devices:
            self.set_device_params(device)

    def get_devices(self):
        devs = []
        for _devs in scan_networks():
            devs.extend(_devs)
        self.set_devices_params(devs)
        return devs

    def alert_blacklist(self, device, connected=True):
        self.send_alert(device, connected)

    def send_alert(self, device, connected=True):
        for alert in self.alerts:
            alert.send_alert(device, connected)

    def disconnect(self, device):
        retries = self.config.get('config', {}).get('disconnect-retries', 3)
        self.disconnect_count[device['mac']] = self.disconnect_count.get(device['mac'], 0) + 1
        if self.disconnect_count[device['mac']] < retries:
            return False
        self.devices_connected = [d for d in self.devices_connected if d != device]
        return True

    def connect(self, device):
        if device not in self.devices_connected:
            self.devices_connected.append(device)

    def check(self):
        self.devices = self.get_devices()
        # Disconnected devices
        for device in substract_lists(self.devices_connected, self.devices):
            if self.disconnect(device) and device['mac'] in self.blacklist:
                self.alert_blacklist(device, False)
        # New connected devices
        for device in substract_lists(self.devices, self.devices_connected):
            if device['mac'] in self.blacklist:
                self.alert_blacklist(device, True)
            self.connect(device)
        # Action for all connected devices now.
        for device in self.devices:
            # Reset disconnect count
            if device['mac'] in self.disconnect_count:
                del self.disconnect_count[device['mac']]

    def start(self):
        while True:
            self.check()
            sleep(self.config.get('config', {}).get('every-seconds', 60))
