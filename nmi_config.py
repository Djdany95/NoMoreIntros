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
    "primaryBackgroundColor": Colour(245, 245, 245),
    "secondaryBackgroundColor": Colour(230, 230, 230),
    "foregroundColor": Colour(72, 72, 72)
}}

config = {"version": 2.1, "language": "es", "theme": "lightTheme"}


## ---------- CONFIG ---------- ##
def get_config():
    try:
        config_file = open('config.json').read()
        config = json.loads(config_file)
        return config
    except:
        set_config()


def set_config():
    with open('config.json', 'w') as config_file:
        json.dump(config, config_file)
        config_file.close()

    get_config()


## ---------- THEME ---------- ##
def get_theme():
    config = get_config()
    return themes.get(config.get("theme"))


def get_theme_name():
    config = get_config()
    return config.get("theme")


def set_theme(theme):
    config = get_config()
    if (get_theme_name() == theme):
        return False
    config["theme"] = theme

    with open('config.json', 'w') as config_file:
        json.dump(config, config_file)
        config_file.close()

    return True


## ---------- LANGUAGE ---------- ##
def get_language():
    config = get_config()
    return config.get("language")


def set_language(language):
    config = get_config()
    if (get_language() == language):
        return False
    config["language"] = language

    with open('config.json', 'w') as config_file:
        json.dump(config, config_file)
        config_file.close()

    return True


## ---------- VERSION ---------- ##
def get_version():
    config = get_config()
    return config.get("version")


def get_latest_version():
    response = urllib.request.urlopen(
        "https://api.github.com/repos/djdany01/nomoreintros/releases/latest").read()
    response = json.loads(response)
    latest_version = {"version": float(response.get("tag_name")), "url": response.get(
        "assets")[0].get("browser_download_url")}
    return latest_version


def set_version(version):
    config = get_config()
    if (get_version() == version):
        return False
    config["version"] = version
    with open('config.json', 'w') as config_file:
        json.dump(config, config_file)
        config_file.close()
    return True


def check_update():
    actual = get_version()
    latest = get_latest_version().get("version")
    if (actual < latest):
        return latest
    else:
        return False


def download_latest_version():
    latest_version = get_latest_version().get("version")
    latestUrl = get_latest_version().get("url")
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    update_file = os.path.join(desktop, "NMI "+str(latest_version)+".exe")
    urllib.request.urlretrieve(latestUrl, update_file)
    set_version(latest_version)
