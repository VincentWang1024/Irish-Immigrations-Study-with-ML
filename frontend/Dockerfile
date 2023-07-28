# Use an official Node runtime as the base image
FROM node:18-alpine

# Set the working directory in the container to /app
WORKDIR /app

# Copy package.json and package-lock.json into the directory /app in the container
COPY package*.json ./

# Install any needed packages specified in package.json
RUN npm install

# Bundle app source inside the Docker image
COPY . .

# Make port 3000 available to the outside 
EXPOSE 3000

# Define the command to run the app
CMD [ "npm", "start" ]
