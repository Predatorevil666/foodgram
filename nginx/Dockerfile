FROM nginx:1.27.4


COPY docs/redoc.html /usr/share/nginx/html/api/docs/redoc.html

COPY nginx/nginx.conf /etc/nginx/templates/default.conf.template

RUN ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime