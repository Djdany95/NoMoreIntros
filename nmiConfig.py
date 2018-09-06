import json
from wx import Colour

themes = {"darkTheme": {
    "primaryBackgroundColor": Colour(45, 48, 53),
    "secondaryBackgroundColor": Colour(35, 37, 41),
    "foregroundColor": Colour(205, 208, 213)
},
    "lightTheme": {
    "primaryBackgroundColor": Colour(250, 250, 250),
    "secondaryBackgroundColor": Colour(230, 230, 230),
    "foregroundColor": Colour(72, 72, 72)
}}


def getTheme():
    configFile = open('config.json').read()
    config = json.loads(configFile)
    return themes.get(config.get("theme"))

def setTheme(theme):
    configFile = open('config.json').read()
    tempFile = json.loads(configFile)
    if(getTheme==theme):
        return False
    tempFile["theme"] = theme

    with open('config.json', 'w') as configFile:
        json.dump(tempFile, configFile)
        configFile.close()

    getTheme()


def getLanguage():
    configFile = open('config.json').read()
    config = json.loads(configFile)
    return config.get("language")

def setLanguage(language):
    configFile = open('config.json').read()
    tempFile = json.loads(configFile)
    if(getLanguage==language):
        return False
    tempFile["language"] = language

    with open('config.json', 'w') as configFile:
        json.dump(tempFile, configFile)
        configFile.close()

    return True


def getVersion():
    configFile = open('config.json').read()
    config = json.loads(configFile)
    return config.get("version")

def setVersion(version):
    configFile = open('config.json').read()
    tempFile = json.loads(configFile)
    if(getVersion==version):
        return False
    tempFile["version"] = version

    with open('config.json', 'w') as configFile:
        json.dump(tempFile, configFile)
        configFile.close()

    return True

getLanguage()