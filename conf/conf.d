server {
    listen 80;
    server_name localhost;

    location /static {
        alias /NHL-Project/flasksite/static;
    }

    location / {
        proxy_pass http:/localhost:8000;
        include /etc/nginx/proxy_params;
        proxy_redirect off;
    }
}
