from influxdb import InfluxDBClient
import time
import datetime
import requests
import re

DB_NAME = 'aio-test'


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
    print("Data written")


def fetch_and_write(db):
    time = datetime.datetime.utcnow()

    r = requests.get('http://192.168.178.23:21710/F0', timeout=3)
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

    print("grid_p: {}".format(grid_p))
    print("load_p: {}".format(load_p))
    print("pv_p: {}".format(pv_p))
    print("inv_p: {}".format(inv_p))
    print("bt_p: {}".format(bt_p))
    print("bt_soc: {}".format(bt_soc))

    write_data(db, time, "grid_p", grid_p)
    write_data(db, time, "load_p", load_p)
    write_data(db, time, "pv_p", pv_p)
    write_data(db, time, "inv_p", inv_p)
    write_data(db, time, "bt_p", bt_p)
    write_data(db, time, "bt_soc", bt_soc)


def main():
    print("Start")

    dbclient = InfluxDBClient(host='localhost', port=8086, username='root', password='root', database=DB_NAME)
    print("Database connection established")

    dbclient.create_database(DB_NAME)
    print("Ensure database: " + DB_NAME)

    #for x in range(0, 10):
    #    write_data(dbclient, datetime.datetime.utcnow(), 'pv', x)
    #    time.sleep(5)

    while True:
        fetch_and_write(dbclient)
        time.sleep(5)


if __name__ == "__main__":
    main()
