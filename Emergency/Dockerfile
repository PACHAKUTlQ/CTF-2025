FROM node:20-alpine
WORKDIR /app
COPY ./src/package*.json ./
RUN npm ci
COPY ./src ./
COPY ./docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT [ "/docker-entrypoint.sh" ]