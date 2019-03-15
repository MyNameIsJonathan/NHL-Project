FROM nickgryg/alpine-pandas

# Add Tini
RUN apk add --update tini

COPY . /app
WORKDIR /app


EXPOSE 8080

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["gunicorn", "-w 3", "-b :8080", "flaskrun:app"]
