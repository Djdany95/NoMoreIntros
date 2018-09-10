import json
import os
import urllib.request
from wx import Colour

themes = {"darkTheme": {
    "name": "darkTheme",
    "primaryBackgroundColor": Colour(45, 48, 53),
    "secondaryBackgroundColor": Colour(35, 37, 41),
    "foregroundColor": Colour(205, 208, 213)
},
    "lightTheme": {
    "name": "lightTheme",
    "primaryBackgroundColor": Colour(250, 250, 250),
    "secondaryBackgroundColor": Colour(230, 230, 230),
    "foregroundColor": Colour(72, 72, 72)
}}

config = {"version": 1.0, "language": "es", "theme": "lightTheme"}

## ---------- CONFIG ---------- ##

def getConfig():
    try:
        configFile = open('config.json').read()
        config = json.loads(configFile)
        return config
    except:
        setConfig()


def setConfig():
    with open('config.json', 'w') as configFile:
        json.dump(config, configFile)
        configFile.close()

    getConfig()

## ---------- THEME ---------- ##

def getTheme():
    config = getConfig()
    return themes.get(config.get("theme"))


def getThemeName():
    config = getConfig()
    return config.get("theme")


def setTheme(theme):
    config = getConfig()
    if(getThemeName() == theme):
        return False
    config["theme"] = theme

    with open('config.json', 'w') as configFile:
        json.dump(config, configFile)
        configFile.close()

    return True

## ---------- LANGUAGE ---------- ##

def getLanguage():
    config = getConfig()
    return config.get("language")


def setLanguage(language):
    config = getConfig()
    if(getLanguage() == language):
        return False
    config["language"] = language

    with open('config.json', 'w') as configFile:
        json.dump(config, configFile)
        configFile.close()

    return True

## ---------- VERSION ---------- ##

def getVersion():
    config = getConfig()
    return config.get("version")

def getLatestVersion():
    response = urllib.request.urlopen(
        "https://api.github.com/repos/djdany01/nomoreintros/releases/latest").read()
    response = json.loads(response)
    latestVersion = {"version": float(response.get("tag_name")), "url": response.get(
        "assets")[0].get("browser_download_url")}
    return latestVersion

def setVersion(version):
    config = getConfig()
    if(getVersion() == version):
        return False
    config["version"] = version
    with open('config.json', 'w') as configFile:
        json.dump(config, configFile)
        configFile.close()
    return True


def checkUpdate():
    actual = getVersion()
    latest = getLatestVersion().get("version")
    if(actual < latest):
        return latest
    else:
        return False

def downloadLatestVersion():
    latestVersion = getLatestVersion().get("version")
    latestUrl = getLatestVersion().get("url")
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    updateFile=os.path.join(desktop, "NoMoreIntros "+str(latestVersion)+".zip")
    urllib.request.urlretrieve(latestUrl, updateFile)
    setVersion(latestVersion)