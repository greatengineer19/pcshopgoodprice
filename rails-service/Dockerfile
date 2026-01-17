# syntax = docker/dockerfile:1

ARG RUBY_VERSION=3.4.7
ARG RAILS_ENV=staging
FROM registry.docker.com/library/ruby:$RUBY_VERSION-slim AS base

WORKDIR /app

ENV RAILS_ENV=$RAILS_ENV \
    BUNDLE_DEPLOYMENT="1" \
    BUNDLE_PATH="/usr/local/bundle" \
    BUNDLE_WITHOUT="development:test"

# Throw-away build stage
FROM base AS build

# Install only essential build packages
RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y \
    build-essential \
    git \
    libpq-dev \
    libyaml-dev \
    pkg-config && \
    rm -rf /var/lib/apt/lists/*

# Install gems with reduced parallelism for t2.micro
COPY Gemfile Gemfile.lock ./
RUN bundle config set --local cache_all false && \
    bundle config set --local clean true && \
    bundle config set --local jobs 1 && \
    bundle install --retry 3 && \
    bundle clean --force && \
    rm -rf ~/.bundle/ \
    "${BUNDLE_PATH}"/ruby/*/cache \
    "${BUNDLE_PATH}"/ruby/*/bundler/gems/*/.git \
    "${BUNDLE_PATH}"/ruby/*/gems/*/test \
    "${BUNDLE_PATH}"/ruby/*/gems/*/spec

# Copy application code
COPY . .

# Precompile bootsnap for faster boot
RUN bundle exec bootsnap precompile app/ lib/

# Clean up unnecessary files
RUN rm -rf .git tmp/cache/* log/* spec test

# Final stage
FROM base

# Install only runtime dependencies
RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y \
    curl \
    libpq5 \
    libyaml-0-2 && \
    rm -rf /var/lib/apt/lists/*

# Copy from build stage
COPY --from=build /usr/local/bundle /usr/local/bundle
COPY --from=build /app /app

# Create non-root user
RUN useradd rails --create-home --shell /bin/bash && \
    mkdir -p db log tmp/pids tmp/sockets && \
    chown -R rails:rails db log tmp

USER rails:rails

# Health check for API
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
    CMD curl -f http://localhost:3000/up || exit 1

ENTRYPOINT ["/app/bin/docker-entrypoint"]

EXPOSE 3000
CMD ["./bin/rails", "server", "-b", "0.0.0.0"]