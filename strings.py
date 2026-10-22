import os
import re

import yaml

languages = {}
languages_present = {}


def get_string(lang: str):
    return languages[lang]


languages["en"] = yaml.safe_load(open(r"./en.yml", encoding="utf8"))
languages_present["en"] = languages["en"]["name"]

for filename in sorted(os.listdir(r"./")):
    if not re.fullmatch(r"[a-z]{2}\.yml", filename):
        continue
    language_name = filename[:-4]
    if language_name == "en":
        continue
    languages[language_name] = yaml.safe_load(open(r"./" + filename, encoding="utf8"))
    for item in languages["en"]:
        if item not in languages[language_name]:
            languages[language_name][item] = languages["en"][item]
    try:
        languages_present[language_name] = languages[language_name]["name"]
    except:
        print("There is some issue with the language file inside bot.")
        exit()
