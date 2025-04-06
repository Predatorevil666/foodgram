FROM nginx:1.27.4


COPY docs/ /usr/share/nginx/html/api/docs/

COPY nginx/nginx.conf /etc/nginx/templates/default.conf.template

RUN ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime