FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install --production

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY src ./src
COPY package.json ./
ENV NODE_ENV=production
ENV USE_MOCK_DATA=true
EXPOSE 4000
CMD ["node", "src/server.js"]
