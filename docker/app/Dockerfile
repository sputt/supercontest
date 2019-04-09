FROM python:2.7

# Chromedriver is necessary to fetch the lines
RUN apt update
RUN apt install -y wget unzip
RUN wget https://chromedriver.storage.googleapis.com/2.41/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip
RUN rm chromedriver_linux64.zip
RUN mv chromedriver /usr/bin/chromedriver
RUN chown root:root /usr/bin/chromedriver
RUN chmod +x /usr/bin/chromedriver

# The compose file mounts the vcs directory to /sc (for persistence and to mirror
# the source on the host), but you must still copy it during build time (this Dockerfile).
# Then, go there and install the app package into the system environment (editably,
# intentionally pointing back to vcs for our source package only).
COPY . /sc
WORKDIR /sc
RUN pip install -e .

# Start the flask app with the uwsgi wrapper
CMD ["uwsgi", "--ini", "./docker/app/uwsgi.ini"]
