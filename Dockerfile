# Frontend Dockerfile for ReactJS
FROM node:18

WORKDIR /app

# Copy package.json and install dependencies
COPY package.json ./
RUN npm install
RUN npm install lucide-react

# Copy frontend code
COPY . .

EXPOSE 3000

CMD ["npm", "start"]

# Frontend Dockerfile for ReactJS
FROM node:18

WORKDIR /app

# Copy package.json and install dependencies
COPY package.json ./
RUN npm install
RUN npm install lucide-react

# Copy frontend code
COPY . .

EXPOSE 3000

CMD ["npm", "start"]
