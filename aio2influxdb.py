from influxdb import InfluxDBClient
import time
import datetime
import requests
import re
import math
import logging
from logging.handlers import WatchedFileHandler
import sys
from pathlib import Path


DB_NAME = 'aio'
AIO_HOST = '192.168.178.23'
FREQUENCY = 10

USE_EXAMPLE = True
EXAMPLE_FILE = 'examples/F0.html'
USE_INFLUXDB = True

MAX_NUMBER_OF_EXCEPTIONS = 5

logs = Path('logs')


def write_data(db, time, measurement, value):
    json_body = [
        {
            "measurement": measurement,
            "time": time,
            "fields": {
                "value": value
            }
        }
    ]
    if db:
        db.write_points(json_body)
        logging.info('Data written: {}: {}'.format(measurement, value))


def fetch_html():
    content = ""

    if USE_EXAMPLE:
        p = Path(EXAMPLE_FILE)
        with p.open("r") as myfile:
            content = myfile.read()

    else:
        timeout = math.floor(FREQUENCY * 0.6)
        r = requests.get("http://{}:21710/F0".format(AIO_HOST), timeout=timeout)
        if r.ok:
            content = r.text

    return content


def parse_and_write(db, html):
    time = datetime.datetime.utcnow()

    if not html:
        return

    measurements = ['GRID_P', 'LOAD_P', 'PV_P', 'INV_P', 'BT_P', 'BT_SOC', 'Temp']

    for measurement in measurements:
        regexp = measurement + r"""</td><td>(-?\d+\.+\d+)</td>"""
        m = re.search(regexp, html)
        if m:
            value = m.group(1)

            write_data(db, time, measurement, value)
        else:
            # measurment not found, safe html for reference
            filepath = logs / "parsing_failed-{}-{}.html".format(time.strftime('%Y_%m_%d-%H_%M_%S'), measurement)
            with filepath.open("w") as myfile:
                myfile.write(html)
            logging.info("Could not find '{}'. Safeing: {}".format(measurement, filepath))


def main():
    logs.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            WatchedFileHandler(str(logs / "aio2influxdb.log")),
            logging.StreamHandler(sys.stdout)
        ])
    logging.info('Startup')

    if EXAMPLE_FILE:
        logging.info('Using example file as source')

    dbclient = None
    if USE_INFLUXDB:
        dbclient = InfluxDBClient(host='localhost', port=8086,
                                  username='root', password='root',
                                  database=DB_NAME)
        logging.info('Database connection established')

        dbclient.create_database(DB_NAME)
        logging.info("Ensure database: " + DB_NAME)

    exceptions = 0
    while exceptions < MAX_NUMBER_OF_EXCEPTIONS:
        try:
            html = fetch_html()
            parse_and_write(dbclient, html)

            time.sleep(FREQUENCY)
        except Exception:
            exceptions = exceptions + 1
            timestring = time.strftime('%Y_%m_%d-%H_%M_%S')
            logging.exception("Exception at " + timestring)

            filepath = logs / "exception-{}.html".format(timestring)
            with filepath.open("w") as myfile:
                myfile.write(html)


if __name__ == "__main__":
    main()
