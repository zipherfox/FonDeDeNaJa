# 🚀 FonDeDeNaJa Web Interface 🚀

## Blazingly Fast Memory Safe OMR Processing with Web UI

This is the web interface for the FonDeDeNaJa OMR (Optical Mark Recognition) processing system, built with **Rust** and **Axum** for maximum performance and memory safety.

## Features

- **🚀 Blazingly Fast**: Built entirely in Rust for maximum performance
- **🔒 Memory Safe**: Zero buffer overflows, memory leaks, or segfaults guaranteed by Rust compiler
- **🌐 Modern Web UI**: Responsive, drag-and-drop interface similar to Streamlit
- **⚡ Real-time Processing**: Live status updates and progress tracking
- **📤 File Upload**: Drag and drop multiple OMR image files
- **🎯 Auto-alignment**: Optional automatic template alignment
- **🔍 Debug Mode**: Detailed processing information and statistics
- **📊 Results Display**: Comprehensive processing summary and file details

## Quick Start

### Start the Web Server

```bash
# Build and run the web interface
cargo build --release
./target/release/fon-de-de-na-ja-web
```

The web interface will be available at: **http://localhost:3000**

### Using the Web Interface

1. **Upload Files**: Drag and drop OMR image files or click to browse
   - Supported formats: JPG, JPEG, PNG, BMP, TIFF

2. **Configure Options**:
   - ✅ **Auto-align images**: Automatically align OMR sheets to template
   - ✅ **Debug mode**: Show detailed processing information

3. **Process**: Click "🚀 Start Processing with Blazing Speed 🚀"

4. **View Results**: Real-time processing status and detailed results

## Web Interface Screenshots

![OMR Web Interface](omr_web_interface.png)

*Modern, responsive web interface with drag-and-drop file upload*

## API Endpoints

The web server provides several REST API endpoints:

- **GET `/`** - Main web interface
- **POST `/upload`** - Upload OMR image files
- **POST `/process`** - Start OMR processing job
- **GET `/status/{job_id}`** - Get processing status
- **GET `/api/health`** - Health check endpoint

## Architecture

- **Frontend**: Pure HTML5/CSS3/JavaScript with modern responsive design
- **Backend**: Rust with Axum web framework
- **Processing**: Multi-threaded OMR processing using Rayon
- **File Handling**: Secure temporary file management
- **Real-time Updates**: Asynchronous job status polling

## Configuration

The web server runs on port 3000 by default. You can modify the configuration in the source code.

### Upload Directories
- **Uploads**: `web_uploads/` - Temporary file storage
- **Results**: `web_results/` - Processing output files

## Performance

The web interface is designed for maximum performance:

- **Concurrent Processing**: Multiple OMR jobs can run simultaneously
- **Memory Efficient**: Rust's zero-cost abstractions and memory safety
- **Fast File I/O**: Asynchronous file operations using Tokio
- **Optimized Frontend**: Minimal JavaScript with efficient DOM manipulation

## Comparison with Streamlit

This Rust web interface provides similar functionality to the original Streamlit implementation with significant advantages:

| Feature | Streamlit (Python) | Rust Web Interface |
|---------|-------------------|-------------------|
| **Performance** | Moderate | 🚀 Blazingly Fast |
| **Memory Safety** | Runtime errors possible | ✅ Compile-time guaranteed |
| **Startup Time** | ~5-10 seconds | ⚡ <1 second |
| **Memory Usage** | High (Python runtime) | 🪶 Minimal |
| **Dependencies** | Heavy Python stack | 📦 Single binary |
| **Concurrency** | Limited (GIL) | 🏆 True parallelism |

## Security

- **Memory Safety**: Rust prevents buffer overflows and memory corruption
- **Secure File Handling**: Temporary file isolation and cleanup
- **Input Validation**: Type-safe request/response handling
- **CORS Protection**: Configurable cross-origin resource sharing

## Development

### Building from Source

```bash
# Install Rust (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Clone and build
git clone <repository>
cd FonDeDeNaJa
cargo build --release --bin fon-de-de-na-ja-web
```

### Dependencies

- **axum**: Web framework with excellent performance
- **tokio**: Asynchronous runtime for non-blocking I/O
- **tower-http**: HTTP middleware for CORS, file serving, and logging
- **serde**: Serialization framework for JSON/API handling
- **uuid**: Unique job identifier generation
- **tracing**: Structured logging and observability

## License

MIT License - See LICENSE file for details.

## Contributing

Contributions welcome! Please ensure all code follows Rust best practices and maintains the high performance standards.

---

*Built with ❤️ and 🚀 by the FonDeDeNaJa team*