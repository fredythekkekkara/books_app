FROM postgres:latest

ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=password
ENV POSTGRES_DB=postgres

COPY init.sql /docker-entrypoint-initdb.d/

VOLUME /var/lib/postgresql/data

EXPOSE 5432
