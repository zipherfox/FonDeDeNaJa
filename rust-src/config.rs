// config.rs - 🚀 Blazingly Fast Configuration Management 🚀

use serde::{Deserialize, Serialize};

/// Processing configuration with optimized defaults for speed 🚀
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProcessingConfig {
    pub dimensions: DimensionConfig,
    pub threshold_params: ThresholdParams,
    pub alignment_params: AlignmentParams,
    pub outputs: OutputConfig,
}

impl Default for ProcessingConfig {
    fn default() -> Self {
        Self {
            dimensions: DimensionConfig::default(),
            threshold_params: ThresholdParams::default(),
            alignment_params: AlignmentParams::default(),
            outputs: OutputConfig::default(),
        }
    }
}

/// Image dimension configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DimensionConfig {
    pub display_width: u32,
    pub display_height: u32,
    pub processing_width: u32,
    pub processing_height: u32,
}

impl Default for DimensionConfig {
    fn default() -> Self {
        Self {
            display_width: 1640,
            display_height: 2480,
            processing_width: 666,
            processing_height: 820,
        }
    }
}

/// Threshold parameters for bubble detection
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ThresholdParams {
    pub gamma_low: f64,
    pub min_gap: u32,
    pub min_jump: u32,
    pub confident_surplus: u32,
    pub jump_delta: u32,
    pub page_type: String,
}

impl Default for ThresholdParams {
    fn default() -> Self {
        Self {
            gamma_low: 0.7,
            min_gap: 30,
            min_jump: 25,
            confident_surplus: 5,
            jump_delta: 30,
            page_type: "white".to_string(),
        }
    }
}

/// Alignment parameters for auto-alignment
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AlignmentParams {
    pub auto_align: bool,
    pub match_col: u32,
    pub max_steps: u32,
    pub stride: u32,
    pub thickness: u32,
}

impl Default for AlignmentParams {
    fn default() -> Self {
        Self {
            auto_align: false,
            match_col: 5,
            max_steps: 20,
            stride: 1,
            thickness: 3,
        }
    }
}

/// Output configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OutputConfig {
    pub show_image_level: u32,
    pub save_image_level: u32,
    pub save_detections: bool,
    pub filter_out_multimarked_files: bool,
}

impl Default for OutputConfig {
    fn default() -> Self {
        Self {
            show_image_level: 0,
            save_image_level: 0,
            save_detections: true,
            filter_out_multimarked_files: false,
        }
    }
}

/// Bubble dimensions for detection
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BubbleDimensions {
    pub width: u32,
    pub height: u32,
}

impl Default for BubbleDimensions {
    fn default() -> Self {
        Self {
            width: 32,
            height: 32,
        }
    }
}