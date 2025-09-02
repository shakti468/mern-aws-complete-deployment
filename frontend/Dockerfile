# Step 1: Build React app
FROM node:18 AS build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Step 2: Serve using Nginx
FROM nginx:alpine

# Copy build files to Nginx html folder
COPY --from=build /app/build /usr/share/nginx/html

# Expose frontend port
EXPOSE 80

# Run nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
