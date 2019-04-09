FROM nginx:latest

# Remove the default nginx conf and copy ours over
RUN rm /etc/nginx/conf.d/default.conf
COPY ./docker/web_server/nginx.conf /etc/nginx/conf.d/
