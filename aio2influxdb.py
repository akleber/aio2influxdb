from influxdb import InfluxDBClient
import time
import datetime
import requests
import re
import math
import logging
import sys


DB_NAME = 'aio-test'
AIO_HOST = '192.168.178.23'
FREQUENCY = 5
TEST_MODE = False


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


def fetch_html():
    content = ""

    if not TEST_MODE:
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
            logging.info('Data written: {}: {}'.format(measurement, value))


def main():
    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            logging.FileHandler("aio2influxdb.log"),
            logging.StreamHandler(sys.stdout)
        ])
    logging.info('Startup')

    dbclient = None
    if not TEST_MODE:
        dbclient = InfluxDBClient(host='localhost', port=8086, username='root', password='root', database=DB_NAME)
        logging.info('Database connection established')

        dbclient.create_database(DB_NAME)
        logging.info("Ensure database: " + DB_NAME)

    while True:
        try:
            html = fetch_html()
            parse_and_write(dbclient, html)

            time.sleep(FREQUENCY)
        except Exception:
            logging.exception("Exception")


if __name__ == "__main__":
    main()
