import json
import yaml
import os

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def load_json(path):
    with open(path) as f:
        return json.load(f)


def main():
    print("=== ESM Demo Runner ===")
    signals = load_yaml(os.path.join(BASE, "config", "signals.yml"))
    features = load_yaml(os.path.join(BASE, "config", "features.yml"))
    policy = load_yaml(os.path.join(BASE, "config", "policy.yml"))
    # Interpret file structure change: use weights instead of initial values
    signal_weights = signals.get("signal_weights", {})
    print("Loaded signals (raw):", signals)
    print("Signal weights:", signal_weights)
    eras_dir = os.path.join(BASE, "examples", "eras")
    eras = {}
    for name in os.listdir(eras_dir):
        era_path = os.path.join(eras_dir, name)
        if os.path.isdir(era_path):
            events_file = os.path.join(era_path, "events.json")
            if os.path.exists(events_file):
                eras[name] = load_json(events_file)
    print("Loaded features:", features)
    print("Loaded policy:", policy)
    print("Available eras:", list(eras.keys()))
    # simple demonstration: show first event impacts of French Revolution if present
    if "french_revolution" in eras:
        ev = eras["french_revolution"]["events"][0]
        print("First event:", ev)


if __name__ == "__main__":
    main()
