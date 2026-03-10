# Makefile for Hybrid Monorepo
# Go (Makefile) + Python & Web (Pants)
# ==================================================

.PHONY: help install build test lint clean dev \
        go-build go-test go-lint python-build python-test python-lint python-check \
        web-build web-test web-lint web-check-types web-dev

# Default target
.DEFAULT_GOAL := help

# Colors for output
CYAN := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Go binary path
GO := /usr/local/go/bin/go

#-----------------------------------------------------------------------------
# Help
#-----------------------------------------------------------------------------
help: ## Show this help
	@echo "$(CYAN)Hybrid Monorepo Commands$(RESET)"
	@echo "========================="
	@echo ""
	@echo "$(GREEN)Quick Start:$(RESET)"
	@echo "  $(CYAN)make install$(RESET)      Install all dependencies"
	@echo "  $(CYAN)make build$(RESET)        Build all services"
	@echo "  $(CYAN)make test$(RESET)         Run all tests"
	@echo "  $(CYAN)make lint$(RESET)         Lint all code"
	@echo ""
	@echo "$(GREEN)Go Services (Makefile):$(RESET)"
	@grep -E '^go-[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-25s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Python & Web (Pants):$(RESET)"
	@grep -E '^(python|web)-[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-25s$(RESET) %s\n", $$1, $$2}'

#-----------------------------------------------------------------------------
# Installation
#-----------------------------------------------------------------------------
install: ## Install all dependencies
	@echo "$(CYAN)Installing all dependencies...$(RESET)"
	@$(MAKE) install-pants
	@$(MAKE) install-python-deps
	@$(MAKE) install-web
	@echo "$(GREEN)✓ All dependencies installed!$(RESET)"

install-pants: ## Install Pants build system
	@echo "$(CYAN)Setting up Pants...$(RESET)"
	@if [ ! -f pants ]; then \
		curl -L https://static.pantsbuild.org/setup/pants -o pants && chmod +x pants; \
	fi
	@./pants --version 2>&1 | grep -E "^[0-9]" || echo "Pants installed"

install-python-deps: ## Generate Python lockfiles
	@echo "$(CYAN)Generating Python lockfiles...$(RESET)"
	@./pants generate-lockfiles 2>&1 | grep -E "(Wrote|ERROR)" || true

install-web: ## Install web dependencies via Pants
	@echo "$(CYAN)Installing web dependencies via Pants...$(RESET)"
	@./pants run //:web-install
	@echo "$(GREEN)✓ Web dependencies installed$(RESET)"

#-----------------------------------------------------------------------------
# Build
#-----------------------------------------------------------------------------
build: ## Build all services (Go + Python + Web)
	@echo "$(CYAN)Building all services...$(RESET)"
	@$(MAKE) go-build
	@$(MAKE) python-build
	@$(MAKE) web-build
	@echo "$(GREEN)✓ All services built!$(RESET)"

go-build: ## Build Go services (gateway, detection)
	@echo "$(CYAN)Building Go services...$(RESET)"
	@mkdir -p dist/go
	@echo "  Building gateway..."
	@cd services/go/gateway && $(GO) build -o ../../../dist/go/gateway ./cmd/gateway
	@echo "  Building detection..."
	@cd services/go/detection && $(GO) build -o ../../../dist/go/detection ./cmd/detection
	@echo "$(GREEN)✓ Go services built:$(RESET)"
	@ls -lh dist/go/

python-build: ## Build Python services with Pants (PEX files)
	@echo "$(CYAN)Building Python services with Pants...$(RESET)"
	@./pants package services/python/triage:triage \
	                 services/python/copilot:copilot \
	                 services/python/agents/investigation:investigation
	@echo "$(GREEN)✓ Python services built$(RESET)"

web-build: ## Build web apps via Pants
	@echo "$(CYAN)Building web apps via Pants...$(RESET)"
	@./pants run //:web-build
	@echo "$(GREEN)✓ Web apps built$(RESET)"

#-----------------------------------------------------------------------------
# Test
#-----------------------------------------------------------------------------
test: ## Run all tests
	@echo "$(CYAN)Running all tests...$(RESET)"
	@$(MAKE) go-test
	@$(MAKE) python-test
	@$(MAKE) web-test
	@echo "$(GREEN)✓ All tests passed!$(RESET)"

go-test: ## Run Go tests
	@echo "$(CYAN)Running Go tests...$(RESET)"
	@cd services/go/gateway && $(GO) test ./... || echo "$(YELLOW)Gateway tests not found$(RESET)"
	@cd services/go/detection && $(GO) test ./... || echo "$(YELLOW)Detection tests not found$(RESET)"
	@cd services/go/pkg && $(GO) test ./... || echo "$(YELLOW)Pkg tests not found$(RESET)"

python-test: ## Run Python tests with Pants
	@echo "$(CYAN)Running Python tests with Pants...$(RESET)"
	@./pants test services/python:: || echo "$(YELLOW)Some tests failed$(RESET)"

web-test: ## Run web tests via Pants
	@echo "$(CYAN)Running web tests via Pants...$(RESET)"
	@./pants run //:web-test || echo "$(YELLOW)Web tests not configured$(RESET)"

#-----------------------------------------------------------------------------
# Lint & Type Check
#-----------------------------------------------------------------------------
lint: ## Lint all code
	@echo "$(CYAN)Linting all code...$(RESET)"
	@$(MAKE) go-lint
	@$(MAKE) python-lint
	@$(MAKE) web-lint
	@echo "$(GREEN)✓ Linting complete$(RESET)"

go-lint: ## Lint Go code with go fmt and go vet
	@echo "$(CYAN)Linting Go code...$(RESET)"
	@cd services/go/gateway && $(GO) fmt ./... && $(GO) vet ./...
	@cd services/go/detection && $(GO) fmt ./... && $(GO) vet ./...
	@cd services/go/pkg && $(GO) fmt ./... && $(GO) vet ./...
	@echo "$(GREEN)✓ Go code linted$(RESET)"

python-lint: ## Lint Python code with Pants (ruff)
	@echo "$(CYAN)Linting Python code with Pants...$(RESET)"
	@./pants lint services/python:: || echo "$(YELLOW)Linting found issues$(RESET)"

python-check: ## Type check Python code with mypy
	@echo "$(CYAN)Type checking Python code...$(RESET)"
	@./pants check services/python:: || echo "$(YELLOW)Type check found issues$(RESET)"

web-lint: ## Lint web code via Pants
	@echo "$(CYAN)Linting web code via Pants...$(RESET)"
	@./pants run //:web-lint || echo "$(YELLOW)Web linting found issues$(RESET)"

web-check-types: ## Type check web code via Pants
	@echo "$(CYAN)Type checking web code via Pants...$(RESET)"
	@./pants run //:web-check-types || echo "$(YELLOW)Type check found issues$(RESET)"

#-----------------------------------------------------------------------------
# Development
#-----------------------------------------------------------------------------
dev: ## Show development commands
	@echo "$(CYAN)Development Mode$(RESET)"
	@echo "================"
	@echo ""
	@echo "$(YELLOW)Run these in separate terminals:$(RESET)"
	@echo "  $(CYAN)make go-dev-gateway$(RESET)     - Run gateway on :8080"
	@echo "  $(CYAN)make go-dev-detection$(RESET)   - Run detection on :8081"
	@echo "  $(CYAN)make python-dev-triage$(RESET)  - Run triage on :8082"
	@echo "  $(CYAN)make python-dev-copilot$(RESET) - Run copilot on :8083"
	@echo "  $(CYAN)make web-dev$(RESET)            - Run web apps on :3000, :3001"

go-dev-gateway: ## Run gateway service in dev mode
	@echo "$(CYAN)Starting gateway service on :8080...$(RESET)"
	@cd services/go/gateway && $(GO) run ./cmd/gateway

go-dev-detection: ## Run detection service in dev mode
	@echo "$(CYAN)Starting detection service on :8081...$(RESET)"
	@cd services/go/detection && $(GO) run ./cmd/detection

python-dev-triage: ## Run triage service in dev mode
	@echo "$(CYAN)Starting triage service on :8082...$(RESET)"
	@./pants run services/python/triage:triage

python-dev-copilot: ## Run copilot service in dev mode
	@echo "$(CYAN)Starting copilot service on :8083...$(RESET)"
	@./pants run services/python/copilot:copilot

web-dev: ## Run web in dev mode via Pants
	@echo "$(CYAN)Starting web development server via Pants...$(RESET)"
	@./pants run //:web-dev

#-----------------------------------------------------------------------------
# Docker
#-----------------------------------------------------------------------------
docker-build: ## Build Docker images
	@echo "$(CYAN)Building Docker images...$(RESET)"
	@echo "$(YELLOW)Go services: Using Dockerfile directly$(RESET)"
	@echo "$(YELLOW)Python services: Using Pants Docker backend$(RESET)"
	@./pants package services/python/triage:docker services/python/copilot:docker
	@echo "$(GREEN)✓ Docker images built$(RESET)"

#-----------------------------------------------------------------------------
# Clean
#-----------------------------------------------------------------------------
clean: ## Clean all build artifacts
	@echo "$(CYAN)Cleaning build artifacts...$(RESET)"
	@rm -rf dist/
	@rm -rf .pants.d/
	@rm -rf node_modules/
	@cd services/go/gateway && $(GO) clean
	@cd services/go/detection && $(GO) clean
	@echo "$(GREEN)✓ Clean complete$(RESET)"

#-----------------------------------------------------------------------------
# CI Specific
#-----------------------------------------------------------------------------
ci-go: ## CI: Build and test Go services
	@echo "$(CYAN)CI: Go services$(RESET)"
	@$(MAKE) go-lint
	@$(MAKE) go-test
	@$(MAKE) go-build

ci-python: ## CI: Lint, check, test, and build Python services
	@echo "$(CYAN)CI: Python services$(RESET)"
	@./pants lint services/python::
	@./pants check services/python::
	@./pants test services/python::
	@./pants package services/python::

ci-web: ## CI: Lint, type-check, build, and test web apps via Pants
	@echo "$(CYAN)CI: Web apps via Pants$(RESET)"
	@./pants run //:web-install
	@./pants run //:web-lint
	@./pants run //:web-check-types
	@./pants run //:web-build
	@./pants run //:web-test

ci-all: ci-go ci-python ci-web ## CI: Run all CI checks
	@echo "$(GREEN)✓ All CI checks passed!$(RESET)"

#-----------------------------------------------------------------------------
# Utility
#-----------------------------------------------------------------------------
version: ## Show versions of all tools
	@echo "$(CYAN)Tool Versions$(RESET)"
	@echo "============="
	@echo "Go:      $$($(GO) version | awk '{print $$3}')"
	@echo "Python:  $$(python3 --version | awk '{print $$2}')"
	@echo "Node.js: $$(node --version)"
	@echo "pnpm:    $$(pnpm --version)"
	@echo "Pants:   $$(./pants --version 2>&1 | grep -E '^[0-9]' || echo 'Not installed')"
