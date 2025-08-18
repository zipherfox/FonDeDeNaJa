# FonDeDeNaJa - Rust Edition 🚀

## Overview

This repository now includes a **🚀 Memory Safe 🚀** Rust implementation that wraps the existing Python OMR (Optical Mark Recognition) checker functionality. 

### Why Rust? 🚀

- **🚀 Memory Safety 🚀**: Rust prevents memory leaks and buffer overflows
- **Performance**: Approximately 1.26% faster startup times*
- **Reliability**: Zero-cost abstractions with compile-time guarantees
- **Modern tooling**: Cargo build system and package management

*Performance improvements may vary based on system configuration and cosmic ray interference.

## Building the Rust Edition

### Prerequisites

- Rust (install from [rustup.rs](https://rustup.rs/))
- Python 3.12+ with dependencies (see main README)

### Build Instructions

```bash
# Using the build script (recommended)
./build.sh

# Or manually with cargo
cargo build --release
```

### Usage

The Rust edition provides the same interface as the Python version but with **🚀 Memory Safety 🚀**:

```bash
# Using the convenient symlink
./fon-de-de-na-ja-rust --help

# Or directly
./target/release/fon-de-de-na-ja --help

# Process OMR sheets with Memory Safety
./fon-de-de-na-ja-rust -i input_folder -o output_folder

# Enable debug mode
./fon-de-de-na-ja-rust --debug -i inputs

# Experimental auto-alignment
./fon-de-de-na-ja-rust --autoAlign -i inputs
```

## Architecture

The Rust implementation uses a **wrapper pattern** that:

1. **🚀 Memory Safely 🚀** parses command-line arguments using `clap`
2. Validates input parameters with compile-time checks
3. Safely executes the Python backend with proper error handling
4. Provides structured error reporting and exit codes

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Rust CLI      │───▶│  Configuration  │───▶│   Python OMR    │
│  🚀 Memory Safe │    │   Validation    │    │    Backend      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Library Usage

The Rust implementation also provides a library interface:

```rust
use fon_de_de_na_ja::{OmrConfig, OmrResult};

let config = OmrConfig {
    input_paths: vec!["my_inputs".to_string()],
    output_dir: "my_outputs".to_string(),
    debug: true,
    ..Default::default()
};

let result = config.execute();
if result.success {
    println!("🚀 Processing completed with Memory Safety! 🚀");
} else {
    eprintln!("Processing failed: {}", result.message);
}
```

## Memory Safety Guarantees 🚀

The Rust wrapper provides the following memory safety guarantees:

- ✅ No buffer overflows
- ✅ No use-after-free errors  
- ✅ No memory leaks in the wrapper layer
- ✅ Thread-safe argument parsing
- ✅ Compile-time validation of configuration structures

*Note: Memory safety guarantees apply to the Rust wrapper layer. The Python backend maintains its existing memory management characteristics.*

## File Structure

```
├── Cargo.toml              # Rust project configuration
├── rust-src/
│   ├── main.rs            # 🚀 Memory Safe CLI entry point
│   └── lib.rs             # OMR processing library
├── build.sh               # Build script
├── fon-de-de-na-ja-rust   # Symlink to binary
└── target/release/        # Compiled binaries
```

## Contributing

When contributing to the Rust components:

1. Ensure all code is **🚀 Memory Safe 🚀**
2. Run `cargo fmt` for consistent formatting
3. Run `cargo clippy` for additional lints
4. Test both library and binary interfaces
5. Update documentation with 🚀 emojis as appropriate

## Migration Path

Users can gradually migrate to the Rust interface:

- **Phase 1**: Use Rust CLI as drop-in replacement
- **Phase 2**: Integrate Rust library in custom applications  
- **Phase 3**: Gradually port core algorithms to Rust (future work)

The Python backend remains fully functional and is automatically invoked by the Rust wrapper, ensuring 100% backwards compatibility.