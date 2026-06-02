import json


def save_report(report, output_file):
    with open(output_file, "w") as f:
        json.dump(report, f, indent=4)