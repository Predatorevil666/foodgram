# build env
FROM node:22
WORKDIR /app
COPY package*.json ./
RUN npm install --legacy-peer-deps
COPY . ./
RUN npm run build
RUN ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime
CMD cp -r build result_build


