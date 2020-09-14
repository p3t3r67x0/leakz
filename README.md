# leakz

> Find plain text passwords in pre compiled hash values like md5, sha1, sha224, sha256, sha384, sha512


### Setup

Next we can install InfluxDB, MonngoDB and Nginx

```sh
sudo apt install influxdb mongodb nginx
```


### Dependencies

Now install the dependencies and activate the virtualenv enviroment

```sh
sudo apt install python3-pip
sudo pip3 install virtualenv
virtualenv -p /usr/bin/python3 venv
source venv/bin/activate
pip3 install setuptools==45
pip3 install -r requirements
```


### Configuration

Here we create a file called `config.json` in the current directory

```json
{
    "MONGO_DB": "intel",
    "MONGO_URI": "127.0.0.1",
    "MONGO_PORT": "27017",
    "MONGO_PASSWORD": "<your secure password>",
    "INFLUX_DB": "metric",
    "INFLUX_URI": "127.0.0.1",
    "INFLUX_PORT": "8086",
    "COSUMER_KEY": "<your twitter key>",
    "COSUMER_SECRET": "<your twitter secret>",
    "ACCEESS_TOKEN_KEY": "<your twitter access token key>",
    "ACCEESS_TOKEN_SECRET": "<your twitter access token secret>"
}
```


Now let's create some users in the MongoDB shell.


```js
use admin
db.createUser({user: "admin", pwd: "<your very strong admin password>", roles: [{ role: "userAdminAnyDatabase", db: "admin" }] })

use intel
db.createUser({user: "pymongo", pwd: "<your very strong mongodb password>", roles: [ "readWrite"]})
```

### Run

Now at this time we are ready to run the server.

```sh
./app.py
```
