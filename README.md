# Hybrid Monorepo

A production-ready hybrid monorepo combining **Go services** (built with Makefile) and **Python backend + Web frontend** (managed by Pants build system).

## Architecture

This monorepo uses a hybrid build approach:

- **Go Services**: Built directly using Makefile and Go toolchain
  - `/services/go/gateway` - API Gateway service
  - `/services/go/detection` - Detection service
  - `/services/go/pkg` - Shared Go packages

- **Python Backend + Web Frontend**: Managed by Pants build system
  - `/services/python/*` - Python microservices (triage, copilot, investigation agent)
  - `/web/` - Web applications built with Next.js and Turborepo
  - `/shared/` - Shared schemas and resources

## Tech Stack

### Go Services
- **Go 1.23.8** - Programming language
- **Makefile** - Build orchestration

### Python Backend
- **Python 3.11.15** - Programming language
- **Pants 2.30.1** - Build system (scie-pants launcher)
- **Ruff** - Linter and formatter
- **MyPy** - Static type checker
- **PEX** - Python executable packaging

### Web Frontend
- **Node.js 18.20.8 LTS** - Runtime
- **pnpm 9.15.9** - Package manager
- **Turborepo** - Build orchestration (wrapped by Pants)
- **Next.js** - React framework
- **TypeScript** - Type-safe JavaScript
- **ESLint** - Linting

## Quick Start

### Prerequisites

- Go 1.23+
- Python 3.11+
- Node.js 18+
- pnpm 9+

### Installation

Install all dependencies:

```bash
make install
```

This will:
1. Set up Pants build system
2. Generate Python dependency lockfiles
3. Install web dependencies via Pants

### Building

Build all services:

```bash
make build
```

Or build specific components:

```bash
make go-build          # Build Go services
make python-build      # Build Python services (PEX files)
make web-build         # Build web apps
```

### Testing

Run all tests:

```bash
make test
```

Or test specific components:

```bash
make go-test           # Test Go services
make python-test       # Test Python services
make web-test          # Test web apps
```

### Linting

Lint all code:

```bash
make lint
```

Or lint specific components:

```bash
make go-lint           # Lint Go code (go fmt + go vet)
make python-lint       # Lint Python code (ruff)
make web-lint          # Lint web code (eslint)
make python-check      # Type check Python (mypy)
make web-check-types   # Type check web (tsc)
```

### Development

Run services in development mode (each in separate terminal):

```bash
# Go services
make go-dev-gateway      # Run gateway on :8080
make go-dev-detection    # Run detection on :8081

# Python services
make python-dev-triage   # Run triage on :8082
make python-dev-copilot  # Run copilot on :8083

# Web apps
make web-dev             # Run web apps on :3000, :3001
```

## Project Structure

```
.
├── Makefile              # Main build orchestration
├── pants.toml            # Pants configuration
├── BUILD.web             # Pants targets for web
├── services/
│   ├── go/               # Go services (Makefile)
│   │   ├── gateway/
│   │   ├── detection/
│   │   └── pkg/
│   └── python/           # Python services (Pants)
│       ├── triage/
│       ├── copilot/
│       └── agents/
├── web/                  # Web monorepo (Pants + Turborepo)
│   ├── apps/
│   │   ├── web/
│   │   └── docs/
│   ├── packages/
│   │   ├── ui/
│   │   ├── eslint-config/
│   │   └── typescript-config/
│   └── turbo.json
└── shared/               # Shared resources
    └── api-schema/
```

## Build System Details

### Why Hybrid?

This monorepo uses different build systems for different languages to optimize for each ecosystem:

1. **Go + Makefile**: Go has excellent built-in tooling, so we use Makefile for simple orchestration
2. **Python + Web + Pants**: Pants provides unified caching, dependency management, and build orchestration for Python and wraps web tools (pnpm/Turborepo)

### About scie-pants Launcher

This project uses **scie-pants**, the next-generation Pants launcher (v0.12.5):

- ✅ **Self-contained**: Bundles its own Python interpreter
- ✅ **GitHub releases**: Pants 2.18+ distributed via GitHub (not PyPI)
- ✅ **Auto-download**: Automatically fetches the version specified in `pants.toml`
- ✅ **Multi-version**: Different projects can use different Pants versions

The `pants` binary in this repo is scie-pants launcher, not the old PyPI-based script.

### How Pants Manages Web

While Pants doesn't have a stable JavaScript backend yet, we use Pants' `run_shell_command` targets to wrap pnpm and Turborepo commands. This provides:

- ✅ Unified build interface (all via `make` or `./pants`)
- ✅ Dependency tracking between Python and Web
- ✅ Consistent CI/CD pipelines
- ✅ Leverages Turborepo's caching under the hood

### Direct Pants Commands

You can also run Pants commands directly:

✅ 명령어
✅ ./pants list     # 타겟 목록 확인
✅ ./pants package  # PEX 빌드
✅ ./pants test     # 테스트 실행
✅ ./pants lint     # 린트 체크
✅ ./pants check    # 타입 체크
✅ ./pants generate-lockfiles # 의존성 재생성 (lockfile 생성)
✅ ./pants run      # 서비스 실행
✅ ./pants dependencies # 의존성 확인
✅ ./pants peek     # 타겟 상세 정보

```bash
# Python services
./pants list services/python::
./pants package services/python/triage:triage
./pants test services/python::
./pants lint services/python::
./pants check services/python::
./pants generate-lockfiles services/python::
./pants run services/python::
./pants dependencies services/python::
./pants peek services/python::

# 린트 및 포맷 (변경됨!)
./pants lint services/python/notification::    # 체크만
./pants fmt services/python/notification::     # 포맷팅
./pants fix services/python/notification::     # 자동 수정 (NEW!)


# Web (via shell commands)
./pants run //:web-install
./pants run //:web-build
./pants run //:web-lint
./pants run //:web-test
```

## CI/CD

The Makefile provides CI-specific targets:

```bash
make ci-go          # CI: Lint, test, build Go
make ci-python      # CI: Lint, check, test, package Python
make ci-web         # CI: Lint, type-check, build, test Web
make ci-all         # CI: Run all checks
```

## Common Commands

```bash
make help           # Show all available commands
make version        # Show tool versions
make clean          # Clean all build artifacts
```

## Configuration Files

- [pants.toml](pants.toml) - Pants build system configuration
- [Makefile](Makefile) - Main build orchestration
- [ruff.toml](ruff.toml) - Python linting configuration
- [mypy.ini](mypy.ini) - Python type checking configuration
- [web/turbo.json](web/turbo.json) - Turborepo configuration

## Developer Guides

### Getting Started
- [Development Setup Guide](docs/development-setup.md) - Complete environment setup with Docker

### Adding Services
- [Adding Go Service](docs/adding-go-service.md) - Step-by-step guide to add new Go services
- [Quick: Add Go Service](docs/quick-add-go-service.md) - Quick reference for adding Go services
- [Adding Python Service](docs/adding-python-service.md) - Step-by-step guide to add new Python services
- [Quick: Add Python Service](docs/quick-add-python-service.md) - Quick reference for adding Python services

## Learn More

- [Pants Build System](https://www.pantsbuild.org/)
- [Go Documentation](https://go.dev/doc/)
- [Turborepo](https://turbo.build/repo)
- [Next.js](https://nextjs.org/)
