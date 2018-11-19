# notes

setting up (spatial) database:

    sudo apt-get install postgis
    sudo apt-get install postgis*

    sudo su - postgres
    psql

    create role "sonicmap";
    alter user "sonicmap" with password 'xxx';
    create database "sonicmap";
    alter role "sonicmap" with login;

enable postgis on database:

    \connect sonicmap
    CREATE EXTENSION postgis;

