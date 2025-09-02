FROM node:18

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Expose port (matches .env PORT=3002)
EXPOSE 3002

CMD ["npm", "start"]
