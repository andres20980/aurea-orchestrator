# Sandbox runner Dockerfile
# This container is used for executing untrusted code in an isolated environment

FROM python:3.11-slim

# Create non-root user for running code
RUN useradd -m -u 1000 -s /bin/bash sandbox

# Set working directory
WORKDIR /workspace

# Install minimal dependencies if needed for common use cases
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Switch to non-root user
USER sandbox

# Default command
CMD ["/bin/bash"]
