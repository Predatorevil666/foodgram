# FROM node:22
# WORKDIR /app
# COPY package*.json ./
# RUN npm install --legacy-peer-deps
# COPY . ./
# RUN npm run build
# RUN ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime
# CMD cp -r build result_build

# FROM node:22
# WORKDIR /app

# COPY package.json package.json
# COPY package-lock.json package-lock.json

# RUN npm ci

# COPY . .
# RUN npm run build
# RUN npm install --global http-server

# RUN ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime

# CMD ["npx", "-y", "http-server", "-p", "9000", "/app/build"]

FROM node:22
WORKDIR /app
COPY package*.json ./
RUN npm install --legacy-peer-deps
COPY . ./
RUN npm run build
RUN ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime
CMD cp -r /app/build/. /frontend_static/