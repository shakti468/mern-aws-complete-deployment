# Base image with Node.js
FROM node:18

# Set working directory inside container
WORKDIR /app

# Copy package.json & package-lock.json first (better for caching)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy rest of the service code
COPY . .

# Expose port (matches .env PORT=3001)
EXPOSE 3001

# Start the app
CMD ["npm", "start"]
