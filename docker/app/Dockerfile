FROM joyzoursky/python-chromedriver:3.7-selenium

# Change the timezone to LA so that python datetime() and such work
# for day verification, pick restriction, etc.
RUN echo America/Los_Angeles >/etc/timezone && ln -sf /usr/share/zoneinfo/America/Los_Angeles /etc/localtime && dpkg-reconfigure -f noninteractive tzdata

# The compose file mounts the vcs directory to /sc (for persistence and to mirror
# the source on the host), but you must still copy it during build time (this Dockerfile).
# Then, go there and install the app package into the system environment (editably,
# intentionally pointing back to vcs for our source package only).
COPY . /sc
WORKDIR /sc
RUN pip install -e . -c compiled-requirements.txt
