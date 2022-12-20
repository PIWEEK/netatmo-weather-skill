from mycroft import MycroftSkill, intent_file_handler


class NetatmoWeather(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('weather.netatmo.intent')
    def handle_weather_netatmo(self, message):
        username = self.settings.get('username')
        self.log.info(f"LOG weather.netatmo username > {username}")

        self.speak_dialog('weather.netatmo')


def create_skill():
    return NetatmoWeather()

