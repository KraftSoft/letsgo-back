apt-get update

apt-get install python3.4
apt-get install python3-pip
apt-get install build-essential python-dev
apt-get install libxml2-dev
apt-get install libxslt1-dev
apt-get install libpq-dev
apt-get install postgresql
apt-get install python-psycopg2
apt-get install postgresql-9.4-postgis-2.1

#apt-get install git
#apt-get install nginx
#apt-get install redis
#apt-get install redis-server
#apt-get install python-pip nginx

pip3 install -r requirements.txt

psql postgres -c "CREATE USER kic WITH PASSWORD '0';"
psql postgres -c "CREATE DATABASE together_db;"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE together_db to kic;"
psql postgres -c "ALTER USER kic SUPERUSER;"
psql postgres -c "CREATE EXTENSION postgis;"