# Use an official Node.js runtime as a parent image
FROM node:18-alpine

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json (if available)
COPY package*.json ./

# Install dependencies (including a static server like 'serve')
RUN npm install && npm install -g serve

# Copy the rest of the application code
COPY . .

# Build the application
RUN npm run build

# Expose port 5482
EXPOSE 5482

# Serve the built application on port 5482
CMD ["serve", "-s", "build", "-l", "5482"]
