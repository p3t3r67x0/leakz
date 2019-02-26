# leakz

Find pre compiled hash values like md5, sha1, sha224, sha256, sha384, sha512 with it's plain text value.


### Setup

The following is an example how to setup on a Ubuntu machine. Add the InfluxData repository to the file `/etc/apt/sources.list.d/influxdb.list`.

```sh
deb https://repos.influxdata.com/ubuntu bionic stable
```

Then we want to import apt key.

```sh
sudo curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -
```

Now we can update and install the InfluxDB.

```sh
sudo apt-get update
sudo apt-get install -y influxdb
```

Then we can install MonngoDB and Nginx.

```sh
sudo apt-get install -y mongodb nginx
```

Next clone this repository and change the directory.

```sh
git clone https://github.com/webtobesocial/leakz.git
cd leakz
```


### Dependencies

Now we want to install the dependencies.

```python
pip install -r requirements
```


### Configuration

Here we create a file called `.config` in the current directory.

```json
{
    "mongodb_db": "intel",
    "mongodb_uri": "localhost",
    "mongodb_port": "27017",
    "influxdb_db": "metric",
    "influxdb_uri": "localhost",
    "influxdb_port": "8086",
    "consumer_key": "<your twitter key>",
    "consumer_secret": "<your twitter secret>",
    "access_token_key": "<your twitter access token key>",
    "access_token_secret": "<your twitter access token secret>"
}
```

Then we create a file called `.secret` with the MongoDB password.

```plaintext
<your very strong mongodb password>
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
