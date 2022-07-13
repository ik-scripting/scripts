#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Fargate version deployed

./faker.py --file <lighthouse.json|percentiles.json>
"""
import argparse, logging, json, random

logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("faker").setLevel(logging.INFO)

def cal_average(num):
    sum_num = 0
    for t in num:
        sum_num = sum_num + t

    avg = sum_num / len(num)
    return round(avg, 2)

def write(file):
    f = open(file, "w")
    if "lighthouse" in file:
        data = [
            {
                "MetricName": "Accessibility",
                "Value": random.randint(70, 92),
                "Unit": "Count"
            },
            {
                "MetricName": "BestPractices",
                "Value": random.randint(55, 99),
                "Unit": "Count"
            },
            {
                "MetricName": "Performance",
                "Value": random.randint(20, 81),
                "Unit": "Count"
            },
            {
                "MetricName": "ProgressiveWebApp",
                "Value": random.randint(27, 69),
                "Unit": "Count"
            },
            {
                "MetricName": "SEO",
                "Value": random.randint(50, 99),
                "Unit": "Count"
            }
        ]
    else:
        _50 = random.randint(80, 165)
        _90 = random.randint(160, 195)
        _95 = random.randint(190, 220)
        avg = cal_average([_50, _90, _95])
        data = [
            {
                "MetricName": "Percentile50%",
                "Value": _50,
                "Unit": "Milliseconds"
            },
            {
                "MetricName": "Percentile90%",
                "Value": _90,
                "Unit": "Milliseconds"
            },
            {
                "MetricName": "Percentile95%",
                "Value": _95,
                "Unit": "Milliseconds"
            },
            {
                "MetricName": "Average",
                "Value": avg,
                "Unit": "Milliseconds"
            }
        ]

    json_data = json.dumps(data, indent=2)
    f.write(json_data)
    f.close()


if __name__ == "__main__":
    logging.info("write to a file...")
    parser = argparse.ArgumentParser(description="write to a file")
    parser.add_argument(
        "-f", "--file", required=True, help="Service name", choices=["lighthouse.json", "percentiles.json"]
    )
    args = parser.parse_args()
    write(file=args.file)
