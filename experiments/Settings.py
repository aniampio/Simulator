import sys
import json
import os

conf = {}

def load(filepath):
    global conf
    print("Settings are being loaded from:%s" % filepath)
    try:
        return json.loads(open(filepath).read())
        # print("Loaded: " + str(conf))
    except Exception:
        print("Scenario file not found!")
        sys.exit(1)

def saveconfig(config, filepath):
    with open(os.path.join(filepath, 'test_config.json'), 'w', encoding='utf-8') as outfile:
        json.dump(config, outfile, ensure_ascii=False, indent=4)
