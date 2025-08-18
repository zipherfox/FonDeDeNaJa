// bubble_detection.rs - 🚀 Blazingly Fast Bubble Detection with Memory Safety 🚀

use anyhow::{Context, Result};
use image::{DynamicImage, ImageBuffer, Luma};
use imageproc::region_labelling::connected_components;
use rayon::prelude::*;
use std::collections::HashMap;

use crate::config::ProcessingConfig;
use crate::template::{OmrTemplate, FieldBlock, BubbleLocation};
use crate::{BubbleResponse};

/// 🚀 Blazingly Fast Bubble Detector 🚀
pub struct BubbleDetector {
    config: ProcessingConfig,
}

impl BubbleDetector {
    /// Create new bubble detector with optimized configuration
    pub fn new(config: &ProcessingConfig) -> Self {
        Self {
            config: config.clone(),
        }
    }

    /// Detect bubbles using template with 🚀 Memory Safety 🚀
    pub fn detect_bubbles_with_template(&self, image: &DynamicImage, template: &OmrTemplate) -> Result<Vec<BubbleResponse>> {
        let gray_img = image.to_luma8();
        let mut responses = Vec::new();

        // Process each field block in parallel for blazing speed 🚀
        let field_responses: Vec<_> = template.field_blocks
            .par_iter()
            .map(|field_block| self.process_field_block(&gray_img, field_block, template))
            .collect::<Result<Vec<_>>>()?;

        responses.extend(field_responses.into_iter().flatten());

        Ok(responses)
    }

    /// Auto-detect bubbles without template
    pub fn detect_bubbles_auto(&self, image: &DynamicImage) -> Result<Vec<BubbleResponse>> {
        let gray_img = image.to_luma8();
        
        // Apply automatic bubble detection algorithm
        let bubble_regions = self.find_bubble_regions(&gray_img)?;
        
        let mut responses = Vec::new();
        for (idx, region) in bubble_regions.iter().enumerate() {
            let confidence = self.calculate_bubble_confidence(&gray_img, region)?;
            
            if confidence > 0.5 {  // Threshold for bubble detection
                responses.push(BubbleResponse {
                    field_label: format!("Auto_Field_{}", idx),
                    detected_values: vec!["MARKED".to_string()],
                    confidence,
                    is_multi_marked: false,
                });
            }
        }

        Ok(responses)
    }

    /// Process individual field block with blazing speed 🚀
    fn process_field_block(&self, image: &ImageBuffer<Luma<u8>, Vec<u8>>, 
                          field_block: &FieldBlock, 
                          template: &OmrTemplate) -> Result<Vec<BubbleResponse>> {
        
        let mut responses = Vec::new();
        let mut detected_values = Vec::new();
        let mut confidences = Vec::new();

        // Check each bubble in the field
        for (bubble_idx, bubble) in field_block.bubbles.iter().enumerate() {
            let bubble_region = self.extract_bubble_region(image, field_block, bubble, template)?;
            let confidence = self.analyze_bubble_marking(&bubble_region)?;
            
            confidences.push(confidence);
            
            // Threshold for considering bubble as marked
            if confidence > 0.6 {
                detected_values.push(bubble.value.clone());
            }
        }

        // Calculate overall confidence
        let avg_confidence = if confidences.is_empty() { 
            0.0 
        } else { 
            confidences.iter().sum::<f64>() / confidences.len() as f64 
        };

        // Check for multi-marking
        let is_multi_marked = detected_values.len() > 1 && 
                             !template.is_multi_choice_field(&field_block.field_label);

        responses.push(BubbleResponse {
            field_label: field_block.field_label.clone(),
            detected_values,
            confidence: avg_confidence,
            is_multi_marked,
        });

        Ok(responses)
    }

    /// Extract bubble region from image
    fn extract_bubble_region(&self, image: &ImageBuffer<Luma<u8>, Vec<u8>>, 
                           field_block: &FieldBlock, 
                           bubble: &BubbleLocation, 
                           template: &OmrTemplate) -> Result<ImageBuffer<Luma<u8>, Vec<u8>>> {
        
        let (img_width, img_height) = image.dimensions();
        let bubble_width = template.bubble_dimensions.width;
        let bubble_height = template.bubble_dimensions.height;

        // Calculate absolute position
        let abs_x = field_block.origin.0 + bubble.position.0;
        let abs_y = field_block.origin.1 + bubble.position.1;

        // Bounds checking with memory safety 🚀
        let start_x = abs_x.min(img_width.saturating_sub(bubble_width));
        let start_y = abs_y.min(img_height.saturating_sub(bubble_height));
        let end_x = (start_x + bubble_width).min(img_width);
        let end_y = (start_y + bubble_height).min(img_height);

        // Extract region
        let mut bubble_region = ImageBuffer::new(end_x - start_x, end_y - start_y);
        
        for y in start_y..end_y {
            for x in start_x..end_x {
                if let Some(pixel) = image.get_pixel_checked(x, y) {
                    bubble_region.put_pixel(x - start_x, y - start_y, *pixel);
                }
            }
        }

        Ok(bubble_region)
    }

    /// Analyze bubble marking with advanced algorithms 🚀
    fn analyze_bubble_marking(&self, bubble_region: &ImageBuffer<Luma<u8>, Vec<u8>>) -> Result<f64> {
        if bubble_region.width() == 0 || bubble_region.height() == 0 {
            return Ok(0.0);
        }

        // Calculate darkness ratio
        let total_pixels = (bubble_region.width() * bubble_region.height()) as f64;
        let mut dark_pixels = 0;
        let mut total_intensity = 0u64;

        for pixel in bubble_region.pixels() {
            let intensity = pixel[0];
            total_intensity += intensity as u64;
            
            // Consider pixel as "dark" if below threshold
            if intensity < 128 {
                dark_pixels += 1;
            }
        }

        let darkness_ratio = dark_pixels as f64 / total_pixels;
        let avg_intensity = total_intensity as f64 / total_pixels;
        
        // Normalized inverse intensity (lower intensity = higher confidence)
        let intensity_confidence = (255.0 - avg_intensity) / 255.0;
        
        // Combined confidence metric
        let confidence = (darkness_ratio * 0.7 + intensity_confidence * 0.3).min(1.0);

        Ok(confidence)
    }

    /// Find bubble regions automatically using computer vision
    fn find_bubble_regions(&self, image: &ImageBuffer<Luma<u8>, Vec<u8>>) -> Result<Vec<BubbleRegion>> {
        // Apply threshold to create binary image
        let binary_img = self.apply_adaptive_threshold(image)?;
        
        // Find connected components (potential bubbles)
        let labeled_image = connected_components(&binary_img, imageproc::region_labelling::Connectivity::Eight, Luma([0u8]));
        
        // Extract regions that could be bubbles
        let mut regions = Vec::new();
        let mut region_map: HashMap<u32, BubbleRegion> = HashMap::new();

        for (y, row) in labeled_image.enumerate_rows() {
            for (x, _, pixel) in row {
                let label = pixel[0];
                if label > 0 {  // Background is 0
                    let region = region_map.entry(label).or_insert_with(|| BubbleRegion::new());
                    region.add_pixel(x as u32, y as u32);
                }
            }
        }

        // Filter regions by size to find likely bubbles
        for region in region_map.into_values() {
            if region.is_likely_bubble() {
                regions.push(region);
            }
        }

        Ok(regions)
    }

    /// Apply adaptive threshold for better bubble detection
    fn apply_adaptive_threshold(&self, image: &ImageBuffer<Luma<u8>, Vec<u8>>) -> Result<ImageBuffer<Luma<u8>, Vec<u8>>> {
        let (width, height) = image.dimensions();
        let mut binary: ImageBuffer<Luma<u8>, Vec<u8>> = ImageBuffer::new(width, height);

        // Simple Otsu-like thresholding
        let threshold = self.calculate_otsu_threshold(image);

        for (src, dst) in image.pixels().zip(binary.pixels_mut()) {
            dst[0] = if src[0] < threshold { 0 } else { 255 };
        }

        Ok(binary)
    }

    /// Calculate Otsu threshold for optimal binarization
    fn calculate_otsu_threshold(&self, image: &ImageBuffer<Luma<u8>, Vec<u8>>) -> u8 {
        // Calculate histogram
        let mut histogram = [0u32; 256];
        for pixel in image.pixels() {
            histogram[pixel[0] as usize] += 1;
        }

        let total_pixels = (image.width() * image.height()) as f64;
        let mut best_threshold = 0u8;
        let mut max_variance = 0.0;

        for threshold in 0..256 {
            let (w0, w1, mu0, mu1) = self.calculate_class_stats(&histogram, threshold, total_pixels);
            
            if w0 > 0.0 && w1 > 0.0 {
                let variance = w0 * w1 * (mu0 - mu1).powi(2);
                if variance > max_variance {
                    max_variance = variance;
                    best_threshold = threshold as u8;
                }
            }
        }

        best_threshold
    }

    /// Calculate class statistics for Otsu threshold
    fn calculate_class_stats(&self, histogram: &[u32; 256], threshold: usize, total_pixels: f64) -> (f64, f64, f64, f64) {
        let mut w0 = 0.0;
        let mut sum0 = 0.0;
        
        for i in 0..threshold {
            w0 += histogram[i] as f64;
            sum0 += (i as f64) * (histogram[i] as f64);
        }
        
        let w1 = total_pixels - w0;
        let sum1: f64 = (threshold..256)
            .map(|i| (i as f64) * (histogram[i] as f64))
            .sum();

        let mu0 = if w0 > 0.0 { sum0 / w0 } else { 0.0 };
        let mu1 = if w1 > 0.0 { sum1 / w1 } else { 0.0 };

        (w0 / total_pixels, w1 / total_pixels, mu0, mu1)
    }

    /// Calculate confidence for detected bubble region
    fn calculate_bubble_confidence(&self, image: &ImageBuffer<Luma<u8>, Vec<u8>>, region: &BubbleRegion) -> Result<f64> {
        // Extract region and analyze
        let (start_x, start_y, end_x, end_y) = region.get_bounds();
        
        if start_x >= end_x || start_y >= end_y {
            return Ok(0.0);
        }

        let width = end_x - start_x;
        let height = end_y - start_y;
        let mut extracted = ImageBuffer::new(width, height);

        for y in start_y..end_y {
            for x in start_x..end_x {
                if let Some(pixel) = image.get_pixel_checked(x, y) {
                    extracted.put_pixel(x - start_x, y - start_y, *pixel);
                }
            }
        }

        self.analyze_bubble_marking(&extracted)
    }
}

/// Represents a potential bubble region
#[derive(Debug, Clone)]
pub struct BubbleRegion {
    pixels: Vec<(u32, u32)>,
    min_x: u32,
    max_x: u32,
    min_y: u32,
    max_y: u32,
}

impl BubbleRegion {
    fn new() -> Self {
        Self {
            pixels: Vec::new(),
            min_x: u32::MAX,
            max_x: 0,
            min_y: u32::MAX,
            max_y: 0,
        }
    }

    fn add_pixel(&mut self, x: u32, y: u32) {
        self.pixels.push((x, y));
        self.min_x = self.min_x.min(x);
        self.max_x = self.max_x.max(x);
        self.min_y = self.min_y.min(y);
        self.max_y = self.max_y.max(y);
    }

    fn is_likely_bubble(&self) -> bool {
        let width = self.max_x.saturating_sub(self.min_x);
        let height = self.max_y.saturating_sub(self.min_y);
        let area = self.pixels.len();

        // Filter by size - typical bubble characteristics
        area > 20 && area < 2000 && width > 5 && height > 5 && width < 100 && height < 100
    }

    fn get_bounds(&self) -> (u32, u32, u32, u32) {
        (self.min_x, self.min_y, self.max_x + 1, self.max_y + 1)
    }
}