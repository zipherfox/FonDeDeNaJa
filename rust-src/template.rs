// template.rs - 🚀 Blazingly Fast Template Management 🚀

use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::Path;

use crate::config::BubbleDimensions;

/// 🚀 Memory Safe OMR Template 🚀
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OmrTemplate {
    pub bubble_dimensions: BubbleDimensions,
    pub page_dimensions: (u32, u32),
    pub field_blocks: Vec<FieldBlock>,
    pub pre_processors: Vec<PreProcessor>,
    pub custom_labels: HashMap<String, String>,
    pub output_columns: Vec<String>,
    pub options: TemplateOptions,
    pub empty_value: String,
}

/// Field block definition for OMR areas
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FieldBlock {
    pub field_label: String,
    pub field_type: FieldType,
    pub origin: (u32, u32),
    pub bubbles: Vec<BubbleLocation>,
    pub labels: Vec<String>,
}

/// Types of OMR fields
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum FieldType {
    #[serde(rename = "QTYPE_MED")]
    MultipleChoice,
    #[serde(rename = "QTYPE_MCQ")]
    SingleChoice,
    #[serde(rename = "QTYPE_INT")]
    Integer,
    #[serde(rename = "QTYPE_ROLL")]
    RollNumber,
}

/// Individual bubble location within a field
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BubbleLocation {
    pub position: (u32, u32),
    pub value: String,
}

/// Pre-processor for image enhancement
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PreProcessor {
    pub name: String,
    pub options: PreProcessorOptions,
}

/// Pre-processor configuration options
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PreProcessorOptions {
    pub morphology: Option<MorphologyConfig>,
    pub median_blur: Option<u32>,
    pub gaussian_blur: Option<f64>,
    pub threshold: Option<ThresholdConfig>,
}

/// Morphological operation configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MorphologyConfig {
    pub operation: String,  // "open", "close", "erode", "dilate"
    pub kernel_shape: String,  // "rect", "ellipse", "cross"
    pub kernel_size: (u32, u32),
}

/// Threshold configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ThresholdConfig {
    pub threshold_type: String,  // "binary", "adaptive"
    pub threshold_value: u8,
    pub max_value: u8,
}

/// Template options
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TemplateOptions {
    pub enable_multi_column_labels: bool,
    pub enable_thinning_preprocessing: bool,
    pub score_variants: HashMap<String, ScoreVariant>,
}

/// Score variant for different marking schemes
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScoreVariant {
    pub correct: f64,
    pub incorrect: f64,
    pub unmarked: f64,
}

impl OmrTemplate {
    /// Load template from JSON file with 🚀 Memory Safety 🚀
    pub fn load<P: AsRef<Path>>(path: P) -> Result<Self> {
        let content = std::fs::read_to_string(path.as_ref())
            .with_context(|| format!("Failed to read template file: {}", path.as_ref().display()))?;
        
        let template: Self = serde_json::from_str(&content)
            .with_context(|| format!("Failed to parse template JSON: {}", path.as_ref().display()))?;
        
        // Validate template
        template.validate()?;
        
        Ok(template)
    }

    /// Validate template configuration
    fn validate(&self) -> Result<()> {
        // Check bubble dimensions
        if self.bubble_dimensions.width == 0 || self.bubble_dimensions.height == 0 {
            anyhow::bail!("Bubble dimensions must be positive");
        }

        // Check page dimensions
        if self.page_dimensions.0 == 0 || self.page_dimensions.1 == 0 {
            anyhow::bail!("Page dimensions must be positive");
        }

        // Validate field blocks
        for field_block in &self.field_blocks {
            if field_block.field_label.is_empty() {
                anyhow::bail!("Field label cannot be empty");
            }
            
            if field_block.bubbles.is_empty() {
                anyhow::bail!("Field block must have at least one bubble");
            }
        }

        Ok(())
    }

    /// Get field block by label
    pub fn get_field_block(&self, label: &str) -> Option<&FieldBlock> {
        self.field_blocks.iter().find(|block| block.field_label == label)
    }

    /// Get all bubble locations for rapid processing 🚀
    pub fn get_all_bubble_locations(&self) -> Vec<(String, Vec<BubbleLocation>)> {
        self.field_blocks
            .iter()
            .map(|block| (block.field_label.clone(), block.bubbles.clone()))
            .collect()
    }

    /// Apply pre-processors to optimize detection 🚀
    pub fn get_preprocessor_chain(&self) -> &[PreProcessor] {
        &self.pre_processors
    }

    /// Check if field requires multi-marking detection
    pub fn is_multi_choice_field(&self, field_label: &str) -> bool {
        if let Some(field_block) = self.get_field_block(field_label) {
            matches!(field_block.field_type, FieldType::MultipleChoice)
        } else {
            false
        }
    }

    /// Get expected bubble count for validation
    pub fn get_expected_bubble_count(&self) -> usize {
        self.field_blocks.iter().map(|block| block.bubbles.len()).sum()
    }
}

impl Default for OmrTemplate {
    fn default() -> Self {
        Self {
            bubble_dimensions: BubbleDimensions::default(),
            page_dimensions: (666, 820),
            field_blocks: vec![],
            pre_processors: vec![],
            custom_labels: HashMap::new(),
            output_columns: vec![],
            options: TemplateOptions {
                enable_multi_column_labels: false,
                enable_thinning_preprocessing: false,
                score_variants: HashMap::new(),
            },
            empty_value: "".to_string(),
        }
    }
}

/// Create a basic template for testing
impl OmrTemplate {
    pub fn create_basic_template() -> Self {
        let mut template = Self::default();
        
        // Add a simple multiple choice field
        template.field_blocks.push(FieldBlock {
            field_label: "Q1".to_string(),
            field_type: FieldType::MultipleChoice,
            origin: (100, 200),
            bubbles: vec![
                BubbleLocation { position: (0, 0), value: "A".to_string() },
                BubbleLocation { position: (50, 0), value: "B".to_string() },
                BubbleLocation { position: (100, 0), value: "C".to_string() },
                BubbleLocation { position: (150, 0), value: "D".to_string() },
            ],
            labels: vec!["A".to_string(), "B".to_string(), "C".to_string(), "D".to_string()],
        });
        
        template.output_columns = vec!["Q1".to_string()];
        
        template
    }
}