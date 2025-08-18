# Makefile for FonDeDeNaJa - Rust Edition 🚀

.PHONY: all build clean install test help rust-only python-deps

# Default target
all: build

# Build the Rust edition
build:
	@echo "🚀 Building FonDeDeNaJa with Memory Safety..."
	cargo build --release
	@echo "✅ Build complete!"
	@echo "🚀 Run with: ./target/release/fon-de-de-na-ja --help"

# Create convenient symlink
install: build
	ln -sf target/release/fon-de-de-na-ja fon-de-de-na-ja-rust
	@echo "🚀 Symlink created: ./fon-de-de-na-ja-rust"

# Build only Rust components (no Python dependencies)
rust-only:
	@echo "🚀 Building Rust components only..."
	cargo build --release

# Install Python dependencies
python-deps:
	@echo "Installing Python dependencies..."
	pip3 install -r requirements.txt
	pip3 install dotmap deepmerge matplotlib freezegun screeninfo pytest pytest-mock

# Run Rust tests
test:
	@echo "🚀 Running Rust tests..."
	cargo test

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	cargo clean
	rm -f fon-de-de-na-ja-rust

# Format Rust code
format:
	cargo fmt

# Run Rust linter
lint:
	cargo clippy -- -D warnings

# Check Rust code
check:
	cargo check

# Display help
help:
	@echo "🚀 FonDeDeNaJa Rust Edition Build System 🚀"
	@echo ""
	@echo "Available targets:"
	@echo "  all        - Build the complete project (default)"
	@echo "  build      - Build Rust wrapper"  
	@echo "  install    - Build and create convenience symlink"
	@echo "  rust-only  - Build only Rust components"
	@echo "  python-deps- Install Python dependencies"
	@echo "  test       - Run Rust tests"
	@echo "  clean      - Clean build artifacts"
	@echo "  format     - Format Rust code"
	@echo "  lint       - Run Rust linter"
	@echo "  check      - Check Rust code"
	@echo "  help       - Show this help"
	@echo ""
	@echo "🚀 Memory Safety Guaranteed! 🚀"