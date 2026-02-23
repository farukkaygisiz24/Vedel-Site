# syntax = docker/dockerfile:1

# Use Node.js 22 LTS
ARG NODE_VERSION=22
FROM node:${NODE_VERSION}-slim AS base

LABEL fly_launch_runtime="Next.js"

# Next.js app lives here
WORKDIR /app

# Set production environment
ENV NODE_ENV="production"


# Throw-away build stage to reduce size of final image
FROM base AS build

# Install packages needed to build node modules
RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y build-essential node-gyp pkg-config python-is-python3

# Install node modules
COPY package-lock.json package.json ./
RUN npm ci --include=dev

# Copy application code
COPY . .

# Build application
RUN npm run build

# Remove development dependencies
RUN npm prune --omit=dev


# Final stage for app image
FROM base

# Copy standalone build output
COPY --from=build /app/.next/standalone ./

# Copy static assets (not included in standalone output)
COPY --from=build /app/.next/static ./.next/static

# Copy public assets (not included in standalone output)
COPY --from=build /app/public ./public

# Start the server
EXPOSE 3000
ENV HOSTNAME="0.0.0.0"
ENV PORT="3000"
CMD ["node", "server.js"]
