FROM ubuntu:22.04

# Prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies (without Go, Node.js, Python - will install separately)
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    make \
    build-essential \
    software-properties-common \
    ca-certificates \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Go 1.23.8
RUN wget https://go.dev/dl/go1.23.8.linux-amd64.tar.gz \
    && tar -C /usr/local -xzf go1.23.8.linux-amd64.tar.gz \
    && rm go1.23.8.linux-amd64.tar.gz
ENV PATH="/usr/local/go/bin:${PATH}"

# Install Node.js 18 LTS (required for pnpm 9)
RUN mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_18.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Python 3.11 (recommended for performance and long-term support)
RUN add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y python3.11 python3.11-distutils python3.11-venv python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.11 as default python3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Install pnpm 9.15.9
RUN npm install -g pnpm@9.15.9

# Set working directory
WORKDIR /workspace

# Install Pants
RUN curl -L https://static.pantsbuild.org/setup/pants -o /usr/local/bin/pants-setup \
    && chmod +x /usr/local/bin/pants-setup

# Default command
CMD ["bash"]
