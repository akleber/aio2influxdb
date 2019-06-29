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
    db.write_points(json_body)


def fetch_and_write(db):
    time = datetime.datetime.utcnow()
    timeout = math.floor(FREQUENCY * 0.6)

    r = requests.get("http://{}:21710/F0".format(AIO_HOST), timeout=timeout)
    content = r.text
    if not r.ok:
        return

    grid_p = 0
    load_p = 0
    pv_p = 0
    inv_p = 0
    bt_p = 0
    bt_soc = 0

    m = re.search(r"""GRID_P</td><td>(-?\d+\.+\d+)</td>""", content)
    if m:
        grid_p = m.group(1)

    m = re.search(r"""LOAD_P</td><td>(-?\d+\.+\d+)</td>""", content)
    if m:
        load_p = m.group(1)

    m = re.search(r"""PV_P</td><td>(-?\d+\.+\d+)</td>""", content)
    if m:
        pv_p = m.group(1)

    m = re.search(r"""INV_P</td><td>(-?\d+\.+\d+)</td>""", content)
    if m:
        inv_p = m.group(1)

    m = re.search(r"""BT_P</td><td>(-?\d+\.+\d+)</td>""", content)
    if m:
        bt_p = m.group(1)

    m = re.search(r"""BT_SOC</td><td>(-?\d+\.+\d+)</td>""", content)
    if m:
        bt_soc = m.group(1)

    write_data(db, time, "grid_p", grid_p)
    write_data(db, time, "load_p", load_p)
    write_data(db, time, "pv_p", pv_p)
    write_data(db, time, "inv_p", inv_p)
    write_data(db, time, "bt_p", bt_p)
    write_data(db, time, "bt_soc", bt_soc)

    logging.info('Data written: {}; {}; {}; {}; {}; {}'.format(grid_p, load_p, pv_p, inv_p, bt_p, bt_soc))


def main():
    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            logging.FileHandler("aio2influxdb.log"),
            logging.StreamHandler(sys.stdout)
        ])
    logging.info('Startup')

    dbclient = InfluxDBClient(host='localhost', port=8086, username='root', password='root', database=DB_NAME)
    logging.info('Database connection established')

    dbclient.create_database(DB_NAME)
    logging.info("Ensure database: " + DB_NAME)

    while True:
        try:
            fetch_and_write(dbclient)
            time.sleep(FREQUENCY)
        except Exception:
            logging.exception("Exception")


if __name__ == "__main__":
    main()
