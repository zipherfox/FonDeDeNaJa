// evaluation.rs - 🚀 Blazingly Fast OMR Evaluation with Memory Safety 🚀

use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

use crate::{BubbleResponse, ProcessedFile};
use crate::template::{ScoreVariant};

/// 🚀 Memory Safe OMR Evaluation Engine 🚀
pub struct EvaluationEngine {
    scoring_config: ScoringConfig,
}

/// Scoring configuration for different evaluation schemes
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScoringConfig {
    pub default_correct: f64,
    pub default_incorrect: f64,
    pub default_unmarked: f64,
    pub custom_variants: HashMap<String, ScoreVariant>,
}

impl Default for ScoringConfig {
    fn default() -> Self {
        Self {
            default_correct: 1.0,
            default_incorrect: -0.25,
            default_unmarked: 0.0,
            custom_variants: HashMap::new(),
        }
    }
}

/// Evaluation result for a single response
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EvaluationResult {
    pub field_label: String,
    pub detected_values: Vec<String>,
    pub correct_answers: Vec<String>,
    pub is_correct: bool,
    pub score: f64,
    pub confidence: f64,
    pub feedback: String,
}

/// Complete evaluation report
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EvaluationReport {
    pub file_path: String,
    pub total_score: f64,
    pub max_possible_score: f64,
    pub percentage: f64,
    pub field_results: Vec<EvaluationResult>,
    pub multi_marked_fields: Vec<String>,
    pub evaluation_time: f64,
}

impl EvaluationEngine {
    /// Create new evaluation engine with 🚀 Memory Safety 🚀
    pub fn new(scoring_config: ScoringConfig) -> Self {
        Self { scoring_config }
    }

    /// Evaluate OMR responses with blazing speed 🚀
    pub fn evaluate_responses(&self, processed_file: &ProcessedFile, 
                            answer_key: &HashMap<String, Vec<String>>) -> Result<EvaluationReport> {
        
        let start_time = std::time::Instant::now();
        let mut field_results = Vec::new();
        let mut total_score = 0.0;
        let mut max_possible_score = 0.0;
        let mut multi_marked_fields = Vec::new();

        for bubble_response in &processed_file.detected_bubbles {
            let evaluation_result = self.evaluate_single_field(bubble_response, answer_key)?;
            
            total_score += evaluation_result.score;
            max_possible_score += self.scoring_config.default_correct;
            
            if bubble_response.is_multi_marked {
                multi_marked_fields.push(bubble_response.field_label.clone());
            }
            
            field_results.push(evaluation_result);
        }

        let percentage = if max_possible_score > 0.0 {
            (total_score / max_possible_score * 100.0).max(0.0)
        } else {
            0.0
        };

        let evaluation_time = start_time.elapsed().as_secs_f64();

        Ok(EvaluationReport {
            file_path: processed_file.file_path.to_string_lossy().to_string(),
            total_score,
            max_possible_score,
            percentage,
            field_results,
            multi_marked_fields,
            evaluation_time,
        })
    }

    /// Evaluate a single field response
    fn evaluate_single_field(&self, bubble_response: &BubbleResponse, 
                            answer_key: &HashMap<String, Vec<String>>) -> Result<EvaluationResult> {
        
        let field_label = &bubble_response.field_label;
        let detected_values = &bubble_response.detected_values;
        
        // Get correct answers for this field
        let correct_answers = answer_key.get(field_label)
            .cloned()
            .unwrap_or_else(Vec::new);

        // Determine if response is correct
        let is_correct = if bubble_response.is_multi_marked {
            false  // Multi-marked responses are always incorrect
        } else if detected_values.is_empty() {
            correct_answers.is_empty()  // Unmarked is correct only if no answer expected
        } else {
            // Check if detected values match correct answers
            detected_values.iter().all(|val| correct_answers.contains(val)) &&
            correct_answers.iter().all(|val| detected_values.contains(val))
        };

        // Calculate score
        let score = self.calculate_score(field_label, detected_values, &correct_answers, is_correct, bubble_response.is_multi_marked)?;

        // Generate feedback
        let feedback = self.generate_feedback(detected_values, &correct_answers, is_correct, bubble_response.is_multi_marked);

        Ok(EvaluationResult {
            field_label: field_label.clone(),
            detected_values: detected_values.clone(),
            correct_answers,
            is_correct,
            score,
            confidence: bubble_response.confidence,
            feedback,
        })
    }

    /// Calculate score for a field response
    fn calculate_score(&self, field_label: &str, detected_values: &[String], 
                      _correct_answers: &[String], is_correct: bool, is_multi_marked: bool) -> Result<f64> {
        
        // Check for custom scoring variant
        let score_variant = self.scoring_config.custom_variants.get(field_label);

        if is_multi_marked {
            // Multi-marked responses get penalty
            Ok(score_variant.map(|v| v.incorrect).unwrap_or(self.scoring_config.default_incorrect))
        } else if detected_values.is_empty() {
            // Unmarked response
            Ok(score_variant.map(|v| v.unmarked).unwrap_or(self.scoring_config.default_unmarked))
        } else if is_correct {
            // Correct response
            Ok(score_variant.map(|v| v.correct).unwrap_or(self.scoring_config.default_correct))
        } else {
            // Incorrect response
            Ok(score_variant.map(|v| v.incorrect).unwrap_or(self.scoring_config.default_incorrect))
        }
    }

    /// Generate human-readable feedback
    fn generate_feedback(&self, detected_values: &[String], correct_answers: &[String], 
                        is_correct: bool, is_multi_marked: bool) -> String {
        
        if is_multi_marked {
            format!("Multi-marked: {} (Correct: {})", 
                   detected_values.join(", "), 
                   correct_answers.join(", "))
        } else if detected_values.is_empty() {
            if correct_answers.is_empty() {
                "Correctly left blank".to_string()
            } else {
                format!("Left blank (Correct: {})", correct_answers.join(", "))
            }
        } else if is_correct {
            format!("Correct: {}", detected_values.join(", "))
        } else {
            format!("Incorrect: {} (Correct: {})", 
                   detected_values.join(", "), 
                   correct_answers.join(", "))
        }
    }

    /// Generate batch evaluation report for multiple files
    pub fn evaluate_batch(&self, processed_files: &[ProcessedFile], 
                         answer_key: &HashMap<String, Vec<String>>) -> Result<BatchEvaluationReport> {
        
        let start_time = std::time::Instant::now();
        let mut individual_reports = Vec::new();
        let mut total_files = 0;
        let mut files_with_multi_marks = 0;
        let mut overall_score_sum = 0.0;
        let mut overall_max_score_sum = 0.0;

        for processed_file in processed_files {
            let report = self.evaluate_responses(processed_file, answer_key)?;
            
            total_files += 1;
            if !report.multi_marked_fields.is_empty() {
                files_with_multi_marks += 1;
            }
            
            overall_score_sum += report.total_score;
            overall_max_score_sum += report.max_possible_score;
            
            individual_reports.push(report);
        }

        let average_percentage = if overall_max_score_sum > 0.0 {
            (overall_score_sum / overall_max_score_sum * 100.0).max(0.0)
        } else {
            0.0
        };

        let evaluation_time = start_time.elapsed().as_secs_f64();

        Ok(BatchEvaluationReport {
            total_files,
            files_with_multi_marks,
            average_percentage,
            total_score: overall_score_sum,
            max_possible_score: overall_max_score_sum,
            individual_reports,
            evaluation_time,
        })
    }

    /// Load answer key from file
    pub fn load_answer_key(path: &std::path::Path) -> Result<HashMap<String, Vec<String>>> {
        let content = std::fs::read_to_string(path)
            .with_context(|| format!("Failed to read answer key: {}", path.display()))?;

        // Support both JSON and CSV formats
        if path.extension().and_then(|s| s.to_str()) == Some("json") {
            let answer_key: HashMap<String, Vec<String>> = serde_json::from_str(&content)
                .context("Failed to parse JSON answer key")?;
            Ok(answer_key)
        } else {
            // Parse CSV format
            Self::parse_csv_answer_key(&content)
        }
    }

    /// Parse CSV answer key format
    fn parse_csv_answer_key(content: &str) -> Result<HashMap<String, Vec<String>>> {
        let mut answer_key = HashMap::new();
        let mut reader = csv::Reader::from_reader(content.as_bytes());

        for result in reader.records() {
            let record = result.context("Failed to read CSV record")?;
            if record.len() >= 2 {
                let field_label = record[0].to_string();
                let answers: Vec<String> = record.iter()
                    .skip(1)
                    .filter(|s| !s.is_empty())
                    .map(|s| s.to_string())
                    .collect();
                answer_key.insert(field_label, answers);
            }
        }

        Ok(answer_key)
    }

    /// Generate detailed statistics
    pub fn generate_statistics(&self, reports: &[EvaluationReport]) -> DetailedStatistics {
        let mut field_stats: HashMap<String, FieldStatistics> = HashMap::new();
        let mut total_correct = 0;
        let mut total_fields = 0;

        for report in reports {
            for field_result in &report.field_results {
                let field_label = &field_result.field_label;
                let stats = field_stats.entry(field_label.clone()).or_insert_with(FieldStatistics::new);
                
                stats.total_responses += 1;
                if field_result.is_correct {
                    stats.correct_responses += 1;
                }
                stats.confidence_sum += field_result.confidence;
                
                total_fields += 1;
                if field_result.is_correct {
                    total_correct += 1;
                }
            }
        }

        // Calculate accuracy for each field
        for stats in field_stats.values_mut() {
            stats.accuracy = if stats.total_responses > 0 {
                stats.correct_responses as f64 / stats.total_responses as f64
            } else {
                0.0
            };
            stats.average_confidence = if stats.total_responses > 0 {
                stats.confidence_sum / stats.total_responses as f64
            } else {
                0.0
            };
        }

        let overall_accuracy = if total_fields > 0 {
            total_correct as f64 / total_fields as f64
        } else {
            0.0
        };

        DetailedStatistics {
            overall_accuracy,
            field_statistics: field_stats,
            total_files: reports.len(),
            total_fields,
        }
    }
}

/// Batch evaluation report
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BatchEvaluationReport {
    pub total_files: usize,
    pub files_with_multi_marks: usize,
    pub average_percentage: f64,
    pub total_score: f64,
    pub max_possible_score: f64,
    pub individual_reports: Vec<EvaluationReport>,
    pub evaluation_time: f64,
}

/// Field-level statistics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FieldStatistics {
    pub total_responses: usize,
    pub correct_responses: usize,
    pub accuracy: f64,
    pub confidence_sum: f64,
    pub average_confidence: f64,
}

impl FieldStatistics {
    fn new() -> Self {
        Self {
            total_responses: 0,
            correct_responses: 0,
            accuracy: 0.0,
            confidence_sum: 0.0,
            average_confidence: 0.0,
        }
    }
}

/// Detailed statistics across all evaluations
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DetailedStatistics {
    pub overall_accuracy: f64,
    pub field_statistics: HashMap<String, FieldStatistics>,
    pub total_files: usize,
    pub total_fields: usize,
}