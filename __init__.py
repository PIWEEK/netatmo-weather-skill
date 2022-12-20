import json
import unidecode
from mycroft import MycroftSkill, intent_file_handler
from lnetatmo import ClientAuth, WeatherStationData


weather_data = None
username = None
password = None
client_id = None
client_secret = None


class NetatmoWeather(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        _load_setting_variables(self)
        _read_netatmo_weather(self)

    @intent_file_handler('weather_netatmo.intent')
    def handle_weather_netatmo(self, message):
        modules_weather_data = _parse_netatmo_weather(weather_data.rawData)
        self.log.info(f"Weather json  > {modules_weather_data.keys()}")

        module = self.get_response("request_module").lower()
        self.log.info(f"Input module  > {module}")

        if module not in modules_weather_data.keys():
            self.speak_dialog('error_module_missing', {'module': module})
        else:
            module_weather = modules_weather_data[module]
            self.log.info(f"Temperature  > {module_weather['Temperature']}")
            self.speak_dialog('weather_netatmo', data={'module': module, 'temp': module_weather["Temperature"]})


def create_skill():
    return NetatmoWeather()


def _load_setting_variables(self):
    global username, password, client_id, client_secret
    username = self.settings.get('username')
    password = self.settings.get('password')
    client_id = self.settings.get('client_id')
    client_secret = self.settings.get('client_secret')


def _read_netatmo_weather(self):
    authorization = ClientAuth(
        clientId=client_id,
        clientSecret=client_secret,
        username=username,
        password=password)

    global weather_data
    weather_data = WeatherStationData(authorization)


def _normalize(text: str) -> str:
    return unidecode.unidecode(text.lower())


def _parse_netatmo_weather(stations_weather_data):
    if len(stations_weather_data) == 0:
        return {}
    else:
        # TODO: consider more stations
        station_data = stations_weather_data[0]

    weather_json = dict()
    weather_json[_normalize(station_data["module_name"])] = station_data["dashboard_data"]

    for module_data in station_data["modules"]:
        weather_json[_normalize(module_data["module_name"])] = module_data["dashboard_data"]

    return weather_json
