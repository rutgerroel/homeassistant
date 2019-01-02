"""
Platform to read a Buderus KM200 unit.
"""
import logging

from custom_components.buderus import (
    DOMAIN, BuderusBridge)
from homeassistant.const import (
    CONF_RESOURCES, TEMP_CELSIUS)
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {}

def setup_platform(hass, config, add_devices, discovery_info=None):

    global SENSOR_TYPES
    SENSOR_TYPES = {
        'return_temperature': [
            'Retourtemperatuur',
            TEMP_CELSIUS,
            'mdi:thermometer',
            '/system/sensors/temperatures/return'
        ],
        'outside_temperature': [
            'Buitentemperatuur',
            TEMP_CELSIUS,
            'mdi:thermometer',
            '/system/sensors/temperatures/outdoor_t1'
        ],
        'supply_temperature': [
            'Aanvoertemperatuur',
            TEMP_CELSIUS,
            'mdi:thermometer',
            '/system/sensors/temperatures/supply_t1'
        ],
         'room_temperature': [
            'Kamertemperatuur',
            TEMP_CELSIUS,
            'mdi:thermometer',
            '/heatingCircuits/hc1/roomtemperature'
        ],
         'heating_current_roomsetpoint': [
            'Huidige temperatuurinstelling',
            TEMP_CELSIUS,
            'mdi:thermometer',
            '/heatingCircuits/hc1/currentRoomSetpoint'
        ],
         'heatsource_modulation': [
            'Modulatie',
            '%',
            'mdi:percent',
            '/system/heatSources/hs1/actualModulation'
        ],
         'pump_modulation': [
            'Pompmodulatie',
            '%',
            'mdi:percent',
            '/system/appliance/CHpumpModulation'
        ],
         'actual_power': [
            'Stroomverbruik',
            'kW',
            'mdi-flash',
            '/heatSources/actualPower'
        ],
         'power_consumption': [
            'Totaal stroomverbuik vandaag',
            'kWh',
            'mdi-flash',
            '/heatSources/energyMonitoring/consumption'
        ],
    }

    bridge = hass.data[DOMAIN]

    sensors = []
    for resource in config[CONF_RESOURCES]:
        sensor_type = resource.lower()

        if sensor_type not in SENSOR_TYPES:
            _LOGGER.warning("Sensor type: %s is not a valid sensor.",
                            sensor_type)
            continue

        sensors.append(
            BuderusSensor(
                name="%s %s" % (bridge.name, SENSOR_TYPES[sensor_type][0]),
                bridge=bridge,
                sensor_type=sensor_type,
                unit=SENSOR_TYPES[sensor_type][1],
                icon=SENSOR_TYPES[sensor_type][2],
                km_id=SENSOR_TYPES[sensor_type][3]
            )
        )

    add_devices(sensors, True)


class BuderusSensor(Entity):
    """Representation of a Buderus sensor."""

    def __init__(self, name, bridge: BuderusBridge, sensor_type, unit, icon, km_id):
        """Initialize the Buderus sensor."""
        self._name = name
        self._bridge = bridge
        self._sensor_type = sensor_type
        self._unit = unit
        self._icon = icon
        self._km_id = km_id
        self._state = None

    @property
    def state(self):
        """Return the state of the entity."""
        return self._state

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return self._icon

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit
        
    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant."""
        _LOGGER.info("Buderus fetching data...")
        plain = self._bridge._get_data(self._km_id)
        if plain is not None:
            data = self._bridge._get_json(plain)
            self._state = self._bridge._get_value(data)
        _LOGGER.info("Buderus fetching data done.")
