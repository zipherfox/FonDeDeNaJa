#!/bin/bash
# build.sh - Memory Safe Build Script 🚀

echo "🚀 Building FonDeDeNaJa with Rust Memory Safety 🚀"

# Build the Rust wrapper
echo "Building Rust wrapper..."
cargo build --release

if [ $? -eq 0 ]; then
    echo "✅ Rust build successful! Memory safety achieved! 🚀"
    echo "Binary location: $(pwd)/target/release/fon-de-de-na-ja"
    
    # Create symlink for easy access
    ln -sf target/release/fon-de-de-na-ja fon-de-de-na-ja-rust
    echo "🚀 Rust executable symlinked as: fon-de-de-na-ja-rust"
    
    echo ""
    echo "🚀 Usage: ./fon-de-de-na-ja-rust --help"
    echo "🚀 Or: ./target/release/fon-de-de-na-ja --help"
else
    echo "❌ Rust build failed"
    exit 1
fi