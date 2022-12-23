import unidecode
from typing import TypedDict
from mycroft import MycroftSkill, intent_file_handler
from lnetatmo import ClientAuth, WeatherStationData, AuthFailure


class Co2Read(TypedDict):
    level: str
    message: str


class NetatmoWeather(MycroftSkill):
    weather_data = None
    username = None
    password = None
    client_id = None
    client_secret = None

    def __init__(self):
        MycroftSkill.__init__(self)
        self.load_setting_variables()
        self.read_netatmo_weather()

    def initialize(self):
        self.settings_change_callback = self.on_settings_changed
        self.on_settings_changed()

    def on_settings_changed(self):
        self.load_setting_variables()

    @intent_file_handler('weather_netatmo.intent')
    def handle_weather_netatmo(self, message):
        self.read_netatmo_weather()

        if not self.weather_data:
            self.speak_dialog('error_auth')
        else:
            modules_weather_data = parse_netatmo_weather(self.weather_data.rawData)
            self.log.info(f"Weather modules  > {list(modules_weather_data.keys())}")

            module = self.get_response("request_module").lower()
            self.log.info(f"Input module  > {module}")

            if module not in modules_weather_data.keys():
                self.speak_dialog('error_module_missing', {'module': module})
            else:
                module_weather = modules_weather_data[module]
                module_temp = module_weather['Temperature']
                module_humidity = module_weather['Humidity']
                self.log.info(f"Temp/Humidity  > {module_temp}ºC {module_humidity}%")
                self.speak_dialog('weather_netatmo', data={
                    'module': module,
                    'temp': module_temp,
                    'humidity': module_humidity
                })
                if "CO2" in module_weather.keys():
                    module_air = module_weather['CO2']
                    self.log.info(f"CO2 level > {module_air}")
                    co2_read = evaluate_air(c02=module_air)
                    self.speak_dialog(
                        'weather_netatmo_air',
                        data={'level': co2_read["level"], 'message': co2_read["message"]}
                    )

    def load_setting_variables(self):
        self.username = self.settings.get('username')
        self.password = self.settings.get('password')
        self.client_id = self.settings.get('client_id')
        self.client_secret = self.settings.get('client_secret')

    def read_netatmo_weather(self):
        try:
            authorization = ClientAuth(
                clientId=self.client_id,
                clientSecret=self.client_secret,
                username=self.username,
                password=self.password
            )
            self.weather_data = WeatherStationData(authorization)
        except AuthFailure:
            self.log.error(f"Authentication error. Please review the skill configuration.")


def create_skill():
    return NetatmoWeather()


def normalizeText(text: str) -> str:
    return unidecode.unidecode(text.lower())


def evaluate_air(c02: float) -> Co2Read:
    if c02 < 1200:
        return Co2Read(level='fine', message='Enjoy the fresh air.')
    if c02 <= 1500:
        return Co2Read(level='a bit high', message='If possible, consider to open a window.')
    if c02 <= 2000:
        return Co2Read(level='high', message="Consider to open a window if you have troubles concentrating.")

    return Co2Read(level='very high', message='Consider to open a window to avoid headaches.')


def parse_netatmo_weather(stations_weather_data):
    if len(stations_weather_data) == 0:
        return {}
    else:
        # TODO: consider more stations
        station_data = stations_weather_data[0]

    weather_json = dict()
    weather_json[normalizeText(station_data["module_name"])] = station_data["dashboard_data"]

    for module_data in station_data["modules"]:
        weather_json[normalizeText(module_data["module_name"])] = module_data["dashboard_data"]

    return weather_json
