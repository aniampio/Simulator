import sys
import json

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
