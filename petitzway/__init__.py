"""
Python module for Z-Way API.

Copyright Fredrik Haglund 2017

More information about Z-Way here http://www.z-wave.me/index.php?id=22

"""

from typing import List
from requests import Session


class GenericDevice(object):
    """Generic Device class."""

    def __init__(self, data: dict, session: Session, prefix: str) -> None:
        """Class init."""
        self._session = session
        self._prefix = prefix
        self._update_attrs(data)

    def update(self) -> None:
        """Update device information from server."""
        data = self._session.get(self._prefix + "/devices/" + self.device_id).\
            json().get('data')
        self._update_attrs(data)

    def _update_attrs(self, data: dict) -> None:
        """Update device attributes."""
        self._data = data
        self.device_id = self._data['id']
        self.title = self._data['metrics'].get('title')
        self.visible = self._data['visibility']
        self.devicetype = self._data['deviceType']
        self.metrics = self._data['metrics']
        self.probetype = self._data['probeType']

    def is_tagged(self, tag: str = None) -> bool:
        """Return device tags."""
        if tag is not None:
            return tag in self._data.get('tags', [])
        return True


class GenericBinaryDevice(GenericDevice):
    """Generic Binary Device class."""

#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)

    def _update_attrs(self, data: dict):
        """Update device attributes."""
        super()._update_attrs(data)
        if data['metrics']['level'] == 'on':
            self._on = True
        elif data['metrics']['level'] == 'off':
            self._on = False
        else:
            self._on = None

    @property
    def is_on(self) -> bool:
        """Is the device on."""
        return self._on


class GenericMultiLevelDevice(GenericDevice):
    """Generic Multi Level Device."""

#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)

    def _update_attrs(self, data: dict) -> None:
        """Update device attributes."""
        super()._update_attrs(data)
        self._level = data['metrics']['level']

    @property
    def level(self) -> int:
        """Get the current level."""
        return self._level


class SensorMultilevel(GenericMultiLevelDevice):
    """Sensor Multilevel Device."""

#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)

    def _update_attrs(self, data: dict) -> None:
        """Update attributes."""
        super()._update_attrs(data)
        self._unit = data['metrics']['scaleTitle']

    @property
    def unit(self) -> int:
        """Get measuring unit."""
        return self._unit


class SwitchBinary(GenericBinaryDevice):
    """Switch Binary class."""

#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)

    @property
    def is_on(self) -> bool:
        """Is the device on."""
        return self._on

    def turn_on(self) -> None:
        """Turn on the device."""
        command = "on"
        self._session.get(self._prefix + "/devices/{}/command/{}".
                          format(self.device_id, command))

    def turn_off(self) -> None:
        """Turn off the device."""
        command = "off"
        self._session.get(self._prefix + "/devices/{}/command/{}".
                          format(self.device_id, command))


class SwitchMultilevel(GenericMultiLevelDevice):
    """Switch Multilevel Device."""

#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)

    def is_on(self) -> bool:
        """Is the device on."""
        return self._level > 0

    def turn_on(self) -> None:
        """Turn the device on."""
        self.level = 255

    def turn_off(self) -> None:
        """Turn the device off."""
        self.level = 0

    @property
    def level(self) -> int:
        """Get the current level."""
        return self._level

    @level.setter
    def level(self, value: int) -> None:
        """Set the level."""
        self._session.get(self._prefix + "/devices/{}/command/exact?level={}".
                          format(self.device_id, value))


class SensorBinary(GenericBinaryDevice):
    """Sensor Binary class."""

#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)


class Controller(object):
    """Z-way Controller class."""

    def __init__(self,
                 baseurl: str,
                 username: str = None,
                 password: str = None) -> None:
        """Init class."""
        self._session = Session()
        self._session.auth = (username, password)
        self._prefix = baseurl + "/ZAutomation/api/v1"
        self.devices = self.get_all_devices()

    def update(self):
        """Update the devices from server."""
        self.devices = self.get_all_devices()
        return True

    def device(self, device_id: str):
        """Get info on one device."""
        for device in self.devices:
            if device.device_id == device_id:
                return device

    def get_all_devices(self) -> List[GenericDevice]:
        """Get all devices from server."""
        response = self._session.get(self._prefix + "/devices")
        all_devices = []
        for device_dict in response.json().get('data').get('devices'):
            if device_dict['permanently_hidden']:
                continue
            if not device_dict['visibility']:
                continue
            all_devices.append(create_device(device_dict, self._session,
                                             self._prefix))
        return all_devices

    def get_device(self, device_id: str) -> GenericDevice:
        """Get single device from server."""
        response = self._session.get(self._prefix + "/devices/" + device_id)
        device_dict = response.json().get('data')
        return create_device(device_dict, self._session, self._prefix)


def create_device(device_dict: dict, session: Session, prefix: str) -> \
        GenericDevice:
    """Create the device in device list."""
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
