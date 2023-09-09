FROM nginx:stable-alpine

COPY default.conf /etc/nginx
COPY default.conf /etc/nginx/conf.d

COPY fullchain.pem /etc/nginx/fullchain.pem
COPY privkey.pem /etc/nginx/privkey.pem

#EXPOSE 8001