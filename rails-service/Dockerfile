# syntax = docker/dockerfile:1

# Make sure RUBY_VERSION matches the Ruby version in .ruby-version and Gemfile
ARG RUBY_VERSION=3.4.7
ARG RAILS_ENV=staging
FROM registry.docker.com/library/ruby:$RUBY_VERSION-slim AS base

# Rails app lives here
WORKDIR /app

# Set production environment
ENV RAILS_ENV=$RAILS_ENV \
    BUNDLE_DEPLOYMENT="1" \
    BUNDLE_PATH="/usr/local/bundle" \
    BUNDLE_WITHOUT="test"

# Throw-away build stage to reduce size of final image
FROM base AS build

# Install packages needed to build gems and clean up in same layer
RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y build-essential git libpq-dev pkg-config libyaml-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/* /tmp/* /var/tmp/*

# Install application gems with aggressive cleanup
COPY Gemfile Gemfile.lock ./
RUN bundle config set --local cache_all false && \
    bundle config set --local clean true && \
    bundle install --jobs 4 --retry 3 && \
    bundle clean --force && \
    rm -rf ~/.bundle/ "${BUNDLE_PATH}"/ruby/*/cache "${BUNDLE_PATH}"/ruby/*/bundler/gems/*/.git "${BUNDLE_PATH}"/ruby/*/gems/*/test "${BUNDLE_PATH}"/ruby/*/gems/*/spec "${BUNDLE_PATH}"/ruby/*/gems/*/features "${BUNDLE_PATH}"/ruby/*/gems/*/*.md "${BUNDLE_PATH}"/ruby/*/gems/*/*.txt && \
    bundle exec bootsnap precompile --gemfile

# Copy application code
COPY . .

RUN mkdir -p tmp/cache tmp/pids tmp/sockets && \
    chmod -R 755 tmp

# Precompile bootsnap code for faster boot times
RUN bundle exec bootsnap precompile app/ lib/

# Precompile assets and clean up temporary files
RUN rm -rf tmp/cache/* node_modules .git

# Final stage for app image
FROM base

# Install packages needed for deployment
RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y curl libpq5 libyaml-0-2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/* /tmp/* /var/tmp/*

# Copy built gems and application code from build stage
COPY --from=build /usr/local/bundle /usr/local/bundle
COPY --from=build /app /app

# Run and own only the runtime files as a non-root user for security
RUN useradd rails --create-home --shell /bin/bash && \
    chown -R rails:rails db log storage tmp
USER rails:rails

HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
    CMD curl -f http://localhost:3000/up || exit 1

# Entrypoint prepares the database.
ENTRYPOINT ["/app/bin/docker-entrypoint"]

# Start the server by default, this can be overwritten at runtime
EXPOSE 3000
CMD ["./bin/rails", "server", "-b", "0.0.0.0"]