# aio2influxdb

## Setup Raspbian 9 - Stretch

* https://www.circuits.dk/install-grafana-influxdb-raspberry/
* https://grafana.com/grafana/download?platform=arm

```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3 supervisor git screen

wget -qO- https://repos.influxdata.com/influxdb.key | sudo apt-key add -
echo "deb https://repos.influxdata.com/debian stretch stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
sudo apt-get update
sudo apt-get install influxdb

wget https://dl.grafana.com/oss/release/grafana-rpi_6.2.4_armhf.deb
sudo apt-get install libfontconfig1
sudo apt --fix-broken install
sudo dpkg -i grafana-rpi_6.2.4_armhf.deb

git clone https://github.com/akleber/aio2influxdb.git
```

## Dashboard

* http://raspberrypi.fritz.box:3000
* Username/Password: admin/admin

