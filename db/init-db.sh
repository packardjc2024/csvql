#!/bin/bash
set -e

source /.env

# Get decryption password 
SECOND_KEY=$(echo $SECOND_KEY | openssl enc -aes-256-cbc -d -base64 -pbkdf2 -pass pass:${FIRST_KEY} -A)

# Use the decryption password to decrypt values in .env file
NEW_PASSWORD=$(echo $DB_PASSWORD | openssl enc -aes-256-cbc -d -base64 -pbkdf2 -pass pass:${SECOND_KEY} -A)

# Start the PostgreSQL service and create the database and user
psql -v ON_ERROR_STOP=1 --username $DB_USER --dbname postgres <<-EOSQL
    ALTER ROLE $DB_USER WITH ENCRYPTED PASSWORD '$NEW_PASSWORD';
    \c $DB_NAME;
    DROP DATABASE IF EXISTS postgres;
EOSQL

# Copy my pg_hba.conf file to require password login and block host server access
rm /var/lib/postgresql/data/pg_hba.conf
cp /tmp/pg_hba.conf /var/lib/postgresql/data/pg_hba.conf