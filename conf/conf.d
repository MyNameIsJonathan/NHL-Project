events { }

http {

    upstream upstream-web {
        server jonathanolson.us;
    }

    server {
        listen 80;
        server_name gunicornservice;

        location / {
	    root /NHL-Project/flasksite/static;
            proxy_pass http://gunicornservice:8000;
            proxy_redirect off;
            proxy_set_header   Host                 $host;
            proxy_set_header   X-Real-IP            $remote_addr;
            proxy_set_header   X-Forwarded-For      $proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Host     $host:443;
            proxy_set_header   X-Forwarded-Server   $host;
            proxy_set_header   X-Forwarded-Port     443;
            proxy_set_header   X-Forwarded-Proto    https;
        }

        error_page 497 https://$host:$server_port$request_uri;

        listen 443 ssl; # managed by Certbot
        ssl_certificate /etc/letsencrypt/live/jonathanolson.us/fullchain.pem; # managed by Certbot
        ssl_certificate_key /etc/letsencrypt/live/jonathanolson.us/privkey.pem; # managed by Certbot
        include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
        ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

    }

    server {
        if ($host = jonathanolson.us) {
            return 301 https://$host$request_uri;
        } # managed by Certbot


        listen 80;
        server_name jonathanolson.us;
        return 404; # managed by Certbot
    }
}
