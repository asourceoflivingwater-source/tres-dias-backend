FROM python:3.13  
 
RUN mkdir /app
 
WORKDIR /app
 
# Set environment variables 
# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
#Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1 
 
# Upgrade pip
RUN pip install poetry
RUN pip install poetry-plugin-export

COPY ../pyproject.toml ../poetry.lock* /app/

# Export dependencies to requirements.txt
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
# Install dependencies
# We copy the requirements file first, so if only the code changes, this layer is cached.
RUN pip install --no-cache-dir -r requirements.txt
 
# Copy the Django project to the container
COPY . /app/
 
# Expose the Django port
EXPOSE 8000
 
# Run Django’s development server
CMD /bin/sh -c "python management_portal/manage.py migrate --noinput && python management_portal/manage.py runserver 0.0.0.0:8000"