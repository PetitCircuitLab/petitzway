from requests import Session
from typing import List

class GenericDevice(object):
    def __init__(self, data: dict, session: Session, prefix: str) -> None:
        self._session = session
        self._prefix = prefix
        self._update_attrs(data)

    def update(self) -> None:
        data = self._session.get(self._prefix + "/devices/" + self.id).json().get('data')
        self._update_attrs(data)

    def _update_attrs(self, data: dict) -> None:
        self._data = data
        self.id = self._data['id']
        self.title = self._data['metrics'].get('title')
        self.visible = self._data['visibility']
        self.devicetype = self._data['deviceType']
        self.metrics = self._data['metrics']
        self.probetype = self._data['probeType']

    def is_tagged(self, tag: str=None) -> bool:
        if tag is not None:
            return tag in self._data.get('tags', [])
        else:
            return True

class GenericBinaryDevice(GenericDevice):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _update_attrs(self, data: dict):
        super()._update_attrs(data)
        if data['metrics']['level'] == 'on':
            self._on = True
        elif data['metrics']['level'] == 'off':
            self._on = False
        else:
            self._on = None

    @property
    def on(self) -> bool:
        return self._on

class GenericMultiLevelDevice(GenericDevice):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _update_attrs(self, data: dict) -> None:
        super()._update_attrs(data)
        self._level = data['metrics']['level']

    @property
    def level(self) -> int:
        return self._level


class SensorMultilevel(GenericMultiLevelDevice):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _update_attrs(self, data: dict) -> None:
        super()._update_attrs(data)
        self._unit = data['metrics']['scaleTitle']

    @property
    def unit(self) -> int:
        return self._unit

class SwitchBinary(GenericBinaryDevice):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def on(self) -> bool:
        return self._on

    @on.setter
    def on(self, value: bool) -> None:
        if value:
            command = "on"
        else:
            command = "off"
        self._session.get(self._prefix + "/devices/{}/command/{}".format(self.id, command))


class SwitchMultilevel(GenericMultiLevelDevice):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def on(self) -> bool:
        return self._level > 0

    @on.setter
    def on(self, value: bool) -> None:
        if value:
            self.level = 255
        else:
            self.level = 0

    @property
    def level(self) -> int:
        return self._level

    @level.setter
    def level(self, value: int) -> None:
        self._session.get(self._prefix + "/devices/{}/command/exact?level={}".format(self.id, value))


class SensorBinary(GenericBinaryDevice):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Controller(object):
    def __init__(self,
                 baseurl: str,
                 username: str=None,
                 password: str=None) -> None:
        #print(baseurl)
        self._session = Session()
        self._session.auth = (username, password)
        self._prefix = baseurl + "/ZAutomation/api/v1"
        self.devices = self.get_all_devices()

    def update(self):
        self.devices = self.get_all_devices()
        return True

    def device(self, device_id: str):
        for device in self.devices:
            if device.id==device_id:
                return device

    def get_all_devices(self) -> List[GenericDevice]:
        response = self._session.get(self._prefix + "/devices")
        all_devices = []
        for device_dict in response.json().get('data').get('devices'):
            if device_dict['permanently_hidden']:
                continue
            if not device_dict['visibility']:
                continue
            all_devices.append(create_device(device_dict, self._session, self._prefix))
        return all_devices

    def get_device(self, device_id: str) -> GenericDevice:
        response = self._session.get(self._prefix + "/devices/" + device_id)
        device_dict = response.json().get('data')
        return create_device(device_dict, self._session, self._prefix)

def create_device(device_dict: dict, session: Session, prefix: str) -> GenericDevice:
    device_class_map = {
        'switchBinary': SwitchBinary,
        'switchMultilevel': SwitchMultilevel,
        'battery': SensorMultilevel,
        'sensorBinary': SensorBinary,
        'sensorMultilevel': SensorMultilevel,
    }
    device_type = device_dict['deviceType']
    cls = device_class_map.get(device_type, GenericDevice)
    return cls(device_dict, session, prefix)
