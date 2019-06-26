from influxdb import InfluxDBClient
import time
import datetime

DB_NAME = 'aio-test'


def writeData(db, time, measurement, value):
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


def main():
    print("Start")

    dbclient = InfluxDBClient(host='localhost', port=8086, username='root', password='root', database=DB_NAME)
    print("Database connection established")

    dbclient.create_database(DB_NAME)
    print("Ensure database: " + DB_NAME)

    for x in range(0, 10):
        writeData(dbclient, datetime.datetime.utcnow(), 'pv', x)
        time.sleep(5)


if __name__ == "__main__":
    main()
