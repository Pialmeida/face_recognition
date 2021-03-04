import json

with open('config.json','r') as f:
    config = json.load(f)

print(json.dumps(config, indent=4, sort_keys=True))