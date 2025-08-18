// lib.rs - Rust Library for OMR processing utilities

use std::path::Path;
use std::process::Command;

/// 🚀 Memory Safe 🚀 OMR processing result
#[derive(Debug)]
pub struct OmrResult {
    pub success: bool,
    pub message: String,
    pub exit_code: i32,
}

/// 🚀 Memory Safe 🚀 OMR processing configuration
#[derive(Debug, Clone)]
pub struct OmrConfig {
    pub input_paths: Vec<String>,
    pub output_dir: String,
    pub debug: bool,
    pub auto_align: bool,
    pub set_layout: bool,
}

impl Default for OmrConfig {
    fn default() -> Self {
        Self {
            input_paths: vec!["inputs".to_string()],
            output_dir: "outputs".to_string(),
            debug: false,
            auto_align: false,
            set_layout: false,
        }
    }
}

impl OmrConfig {
    /// Execute OMR processing with 🚀 Memory Safety 🚀
    pub fn execute(&self) -> OmrResult {
        let current_dir = std::env::current_dir().unwrap_or_default();
        let python_script = current_dir.join("OMRChecker_main.py");

        let mut cmd = Command::new("python3");
        cmd.arg(&python_script);

        // Add input directories
        for input in &self.input_paths {
            cmd.arg("-i").arg(input);
        }

        // Add output directory
        cmd.arg("-o").arg(&self.output_dir);

        // Add flags
        if self.debug {
            cmd.arg("-d");
        }

        if self.auto_align {
            cmd.arg("-a");
        }

        if self.set_layout {
            cmd.arg("-l");
        }

        match cmd.output() {
            Ok(output) => {
                let success = output.status.success();
                let exit_code = output.status.code().unwrap_or(-1);
                let message = if success {
                    "🚀 OMR Processing completed successfully with Memory Safety! 🚀".to_string()
                } else {
                    format!("OMR Processing failed with exit code: {}", exit_code)
                };

                OmrResult {
                    success,
                    message,
                    exit_code,
                }
            }
            Err(e) => OmrResult {
                success: false,
                message: format!("Failed to execute OMR processing: {}", e),
                exit_code: -1,
            },
        }
    }

    /// Check if Python backend is available
    pub fn check_backend() -> bool {
        let current_dir = std::env::current_dir().unwrap_or_default();
        let python_script = current_dir.join("OMRChecker_main.py");
        Path::new(&python_script).exists()
    }
}
