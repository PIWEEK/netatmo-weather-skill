from mycroft import MycroftSkill, intent_file_handler


class NetatmoWeather(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('weather.netatmo.intent')
    def handle_weather_netatmo(self, message):
        self.speak_dialog('weather.netatmo')


def create_skill():
    return NetatmoWeather()

