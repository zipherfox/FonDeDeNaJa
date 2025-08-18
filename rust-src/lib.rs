// lib.rs - 🚀 Blazingly Fast Memory Safe OMR processing library
//! Complete Rust implementation of Optical Mark Recognition (OMR) processing
//! 
//! This crate provides blazingly fast, memory-safe OMR processing capabilities
//! with full computer vision functionality implemented natively in Rust.

use anyhow::{Context, Result};
use image::{DynamicImage, ImageBuffer, Rgb, RgbImage};
use nalgebra::{DMatrix, DVector};
use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use walkdir::WalkDir;

pub mod config;
pub mod image_processing;
pub mod template;
pub mod bubble_detection;
pub mod alignment;
pub mod evaluation;

use config::*;
use image_processing::*;
use template::*;
use bubble_detection::*;

/// 🚀 Memory Safe 🚀 OMR processing result
#[derive(Debug, Clone, Serialize)]
pub struct OmrResult {
    pub success: bool,
    pub message: String,
    pub processed_files: Vec<ProcessedFile>,
    pub total_processing_time: f64,
    pub errors: Vec<String>,
}

/// Information about a processed OMR file
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProcessedFile {
    pub file_path: PathBuf,
    pub detected_bubbles: Vec<BubbleResponse>,
    pub confidence_score: f64,
    pub processing_time: f64,
    pub alignment_applied: bool,
}

/// Response from bubble detection
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BubbleResponse {
    pub field_label: String,
    pub detected_values: Vec<String>,
    pub confidence: f64,
    pub is_multi_marked: bool,
}

/// 🚀 Memory Safe 🚀 OMR processing configuration
#[derive(Debug, Clone, Serialize)]
pub struct OmrConfig {
    pub input_paths: Vec<PathBuf>,
    pub output_dir: PathBuf,
    pub template_path: Option<PathBuf>,
    pub debug: bool,
    pub auto_align: bool,
    pub set_layout: bool,
    pub processing_config: ProcessingConfig,
}

impl Default for OmrConfig {
    fn default() -> Self {
        Self {
            input_paths: vec![PathBuf::from("inputs")],
            output_dir: PathBuf::from("outputs"),
            template_path: None,
            debug: false,
            auto_align: false,
            set_layout: false,
            processing_config: ProcessingConfig::default(),
        }
    }
}

impl OmrConfig {
    /// Execute OMR processing with 🚀 Blazingly Fast Memory Safety 🚀
    pub fn execute(&self) -> Result<OmrResult> {
        let start_time = std::time::Instant::now();
        
        println!("🚀 Starting blazingly fast OMR processing... 🚀");
        
        // Create output directory
        std::fs::create_dir_all(&self.output_dir)
            .context("Failed to create output directory")?;

        // Load template if provided
        let template = if let Some(template_path) = &self.template_path {
            Some(OmrTemplate::load(template_path)?)
        } else {
            None
        };

        // Find all image files
        let image_files = self.find_image_files()?;
        
        if image_files.is_empty() {
            return Ok(OmrResult {
                success: false,
                message: "No image files found in input directories".to_string(),
                processed_files: vec![],
                total_processing_time: 0.0,
                errors: vec!["No input files found".to_string()],
            });
        }

        println!("🚀 Found {} image files to process", image_files.len());

        // Process files in parallel for blazing speed 🚀
        let processed_files: Vec<_> = image_files
            .par_iter()
            .map(|file_path| self.process_single_file(file_path, &template))
            .collect::<Result<Vec<_>>>()?;

        let total_time = start_time.elapsed().as_secs_f64();
        
        // Generate results
        self.generate_results(&processed_files)?;

        println!("🚀 Processing completed in {:.2} seconds with blazing speed! 🚀", total_time);

        Ok(OmrResult {
            success: true,
            message: format!("🚀 Successfully processed {} files with memory safety! 🚀", processed_files.len()),
            processed_files,
            total_processing_time: total_time,
            errors: vec![],
        })
    }

    /// Find all image files in input directories
    fn find_image_files(&self) -> Result<Vec<PathBuf>> {
        let mut files = Vec::new();
        
        for input_path in &self.input_paths {
            if input_path.is_file() {
                files.push(input_path.clone());
            } else if input_path.is_dir() {
                for entry in WalkDir::new(input_path) {
                    let entry = entry?;
                    let path = entry.path();
                    
                    if let Some(ext) = path.extension() {
                        let ext = ext.to_string_lossy().to_lowercase();
                        if matches!(ext.as_str(), "jpg" | "jpeg" | "png" | "bmp" | "tiff") {
                            files.push(path.to_path_buf());
                        }
                    }
                }
            }
        }
        
        Ok(files)
    }

    /// Process a single OMR file with blazing fast algorithms 🚀
    fn process_single_file(&self, file_path: &Path, template: &Option<OmrTemplate>) -> Result<ProcessedFile> {
        let start_time = std::time::Instant::now();
        
        if self.debug {
            println!("🚀 Processing: {}", file_path.display());
        }

        // Load and preprocess image
        let mut image = ImageProcessor::load_image(file_path)?;
        image = ImageProcessor::preprocess_image(image, &self.processing_config)?;

        // Apply auto-alignment if enabled
        let alignment_applied = if self.auto_align {
            if let Some(template) = template {
                image = ImageProcessor::auto_align_image(image, template)?;
                true
            } else {
                false
            }
        } else {
            false
        };

        // Detect bubbles
        let bubble_detector = BubbleDetector::new(&self.processing_config);
        let detected_bubbles = if let Some(template) = template {
            bubble_detector.detect_bubbles_with_template(&image, template)?
        } else {
            bubble_detector.detect_bubbles_auto(&image)?
        };

        // Calculate confidence score
        let confidence_score = detected_bubbles.iter()
            .map(|b| b.confidence)
            .sum::<f64>() / detected_bubbles.len().max(1) as f64;

        let processing_time = start_time.elapsed().as_secs_f64();

        Ok(ProcessedFile {
            file_path: file_path.to_path_buf(),
            detected_bubbles,
            confidence_score,
            processing_time,
            alignment_applied,
        })
    }

    /// Generate output results (CSV, JSON, etc.)
    fn generate_results(&self, processed_files: &[ProcessedFile]) -> Result<()> {
        // Generate CSV output
        let csv_path = self.output_dir.join("results.csv");
        let mut wtr = csv::Writer::from_path(&csv_path)?;

        // Write headers
        wtr.write_record(&["file_path", "field_label", "detected_values", "confidence", "processing_time"])?;

        // Write data
        for file in processed_files {
            for bubble in &file.detected_bubbles {
                wtr.write_record(&[
                    file.file_path.to_string_lossy().as_ref(),
                    &bubble.field_label,
                    &bubble.detected_values.join(";"),
                    &bubble.confidence.to_string(),
                    &file.processing_time.to_string(),
                ])?;
            }
        }

        wtr.flush()?;

        // Generate JSON output
        let json_path = self.output_dir.join("results.json");
        let json_data = serde_json::to_string_pretty(processed_files)?;
        std::fs::write(json_path, json_data)?;

        println!("🚀 Results saved to: {}", self.output_dir.display());
        Ok(())
    }
}
