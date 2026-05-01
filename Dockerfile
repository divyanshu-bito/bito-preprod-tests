# Category 10 violation: pulling unsigned, untagged base image
FROM node:latest

WORKDIR /app
COPY . .

# Category 10 violation: piping curl directly into shell from non-verified source
RUN curl http://random-mirror.example.com/install.sh | sh
RUN npm install --production --no-package-lock

# Category 5 violation: running as root in production
USER root
CMD ["node", "src/api/public.js"]
