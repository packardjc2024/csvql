# Pull Python Image
FROM postgres:latest

# Update packages
RUN apt-get update && apt-get install -y postgresql-client nano curl

# Copy the .env file
COPY .env /.env

# Copy the pg_hba.conf file
COPY pg_hba.conf /tmp/pg_hba.conf

# Copy initialization scripts if needed
COPY init-db.sh /docker-entrypoint-initdb.d/
