FROM python:3.7

# Chromedriver prerequisities to fetch the lines
# (ref https://tecadmin.net/setup-selenium-chromedriver-on-ubuntu/)
# Section 1: chromedriver itself
RUN apt-get update
RUN apt-get install -y wget unzip libnss3
RUN wget https://chromedriver.storage.googleapis.com/2.41/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip
RUN rm chromedriver_linux64.zip
RUN mv chromedriver /usr/bin/chromedriver
RUN chown root:root /usr/bin/chromedriver
RUN chmod +x /usr/bin/chromedriver
# Section #2: chrome
RUN curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add
RUN echo "deb [arch=amd64]  http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
RUN apt-get update
RUN apt-get install -y google-chrome-stable

# The compose file mounts the vcs directory to /sc (for persistence and to mirror
# the source on the host), but you must still copy it during build time (this Dockerfile).
# Then, go there and install the app package into the system environment (editably,
# intentionally pointing back to vcs for our source package only).
COPY . /sc
WORKDIR /sc
RUN pip install -e .
