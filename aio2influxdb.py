from influxdb import InfluxDBClient
import time
import datetime

DB_NAME = aio-test

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
    dbclient.write_points(json_body)

def main():
    print("Start")

    dbclient = InfluxDBClient('localhost', 8086, 'root', 'root', 'aio')
    print("Database connection established")

    client.create_database(DB_NAME)
    print("Ensure database: " + DB_NAME)

    for x in range(0, 10):
        time = datetime.datetime.utcnow()
        writeData(dbclient, time, pv, x)
        time.sleep(5)

if __name__ == "__main__":
    main()
