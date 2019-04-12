events { }

http {

    upstream upstream-web {
        server jonathanolson.us;
    }

    server {
        listen 80;
        server_name gunicornservice;

        location /static {
            alias /NHL-Project/flasksite/static;
        }

        location / {
            proxy_pass http://gunicornservice:8000;
            # include /etc/nginx/proxy_params;
            proxy_redirect off;
            proxy_set_header   Host $host;
            proxy_set_header   X-Real-IP $remote_addr;
            proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Host $server_name;
        }
    }
}
