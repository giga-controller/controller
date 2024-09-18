FROM node:18-alpine

RUN apk add --no-cache libc6-compat

WORKDIR /app

COPY package.json ./
COPY package-lock.json ./
COPY .env ./

RUN npm ci

COPY *.ts ./
COPY *.mjs ./
COPY *.js ./
COPY tsconfig.json ./
COPY components.json ./
COPY src ./src
COPY public ./public

ENV NODE_ENV=development

EXPOSE 3000

CMD ["npm", "run", "dev"]


