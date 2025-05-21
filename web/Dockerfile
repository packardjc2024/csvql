# Pull Python Image
FROM python:3.13-slim

# Set work directory
WORKDIR /app

# Update packages
RUN apt-get update && apt-get install -y postgresql-client sudo passwd nano

# Upgrade Pip
RUN pip3 install --upgrade pip

# Install dependencies
COPY requirements.txt /app/
RUN pip3 install -r requirements.txt

# Expose the container's port to the nginx server
EXPOSE 8004

# Copy project
COPY . /app

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Grant permissions to the entrypoint bash file
COPY entry.sh /entry.sh
RUN chmod +x /entry.sh

# Run the entrypoint bash file
ENTRYPOINT ["/entry.sh"]

# # Change container permissions
RUN chown -R www-data:www-data /app
RUN chmod -R 777 /app
USER www-data

# Start the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8004", "csvql.wsgi:application"]