import unidecode
from mycroft import MycroftSkill, intent_file_handler
from lnetatmo import ClientAuth, WeatherStationData, AuthFailure


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
        self.read_netatmo_weather()

    @intent_file_handler('weather_netatmo.intent')
    def handle_weather_netatmo(self, message):
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
                self.log.info(f"Temperature  > {module_weather['Temperature']}")
                self.speak_dialog('weather_netatmo', data={'module': module, 'temp': module_weather["Temperature"]})

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
