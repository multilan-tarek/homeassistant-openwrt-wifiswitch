from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.device_registry import format_mac
from homeassistant.helpers.entity import DeviceInfo
import paramiko
import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'openwrt_wifi_switch'


def setup_platform(hass: HomeAssistant,
                   config: ConfigType,
                   add_entities: AddEntitiesCallback,
                   discovery_info: DiscoveryInfoType | None = None
                   ) -> None:
    for device in hass.data[DOMAIN]["devices"]:
        add_entities([WifiSwitch(device)])


class WifiSwitch(SwitchEntity):
    def __init__(self, device):
        self._attr_is_on = False
        self._device = device

    @property
    def name(self) -> str:
        return "%s-%s" % (self._device["host"], self._device["ifname"])

    @property
    def icon(self) -> str:
        return "mdi:wifi-strength-4"

    @property
    def unique_id(self) -> str:
        return "%s_%s" % (self._device["host"], self._device["ifname"])

    @property
    def is_on(self) -> bool:
        ssh = paramiko.SSHClient()
        ssh.connect(hostname="%s:%s" % (self._device["hostname"], self._device["hostname"]), username=self._device["username"], password=self._device["password"])
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("uci get wireless.%s.disabled" % self._device["ifname"])
        _LOGGER.error(ssh_stdin)
        _LOGGER.error(ssh_stdout)
        _LOGGER.error(ssh_stderr)

        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        ssh = paramiko.SSHClient()
        ssh.connect(hostname="%s:%s" % (self._device["hostname"], self._device["hostname"]), username=self._device["username"], password=self._device["password"])
        ssh.exec_command("uci set wireless.%s.disabled=0" % self._device["ifname"])
        ssh.exec_command("uci commit wireless")
        # ssh.exec_command("wifi")

    async def async_turn_off(self, **kwargs: Any) -> None:
        ssh = paramiko.SSHClient()
        ssh.connect(hostname="%s:%s" % (self._device["hostname"], self._device["hostname"]), username=self._device["username"], password=self._device["password"])
        ssh.exec_command("uci set wireless.%s.disabled=1" % self._device["ifname"])
        ssh.exec_command("uci commit wireless")
        #ssh.exec_command("wifi")