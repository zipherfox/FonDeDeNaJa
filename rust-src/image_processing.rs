// image_processing.rs - 🚀 Blazingly Fast Image Processing with Memory Safety 🚀

use anyhow::{Context, Result};
use image::{DynamicImage, ImageBuffer, Luma, Rgb, RgbImage};
use imageproc::geometric_transformations::{warp, Projection};
use std::path::Path;

use crate::config::ProcessingConfig;
use crate::template::OmrTemplate;

/// 🚀 Blazingly Fast Image Processor 🚀
pub struct ImageProcessor;

impl ImageProcessor {
    /// Load image with memory safety guarantees
    pub fn load_image(path: &Path) -> Result<DynamicImage> {
        let img = image::open(path)
            .with_context(|| format!("Failed to load image: {}", path.display()))?;
        Ok(img)
    }

    /// Preprocess image for optimal OMR detection 🚀
    pub fn preprocess_image(mut img: DynamicImage, config: &ProcessingConfig) -> Result<DynamicImage> {
        // Resize to processing dimensions for blazing speed
        img = img.resize_exact(
            config.dimensions.processing_width,
            config.dimensions.processing_height,
            image::imageops::FilterType::Lanczos3,
        );

        // Convert to grayscale for faster processing
        let gray_img = img.to_luma8();
        
        // Apply gaussian blur for noise reduction
        let blurred = Self::gaussian_blur_image(&gray_img, 1.5)?;
        
        // Normalize image for consistent processing
        let normalized = Self::normalize_image(&blurred);
        
        // Apply gamma correction
        let gamma_corrected = Self::apply_gamma_correction(&normalized, config.threshold_params.gamma_low);
        
        Ok(DynamicImage::ImageLuma8(gamma_corrected))
    }

    /// Apply gaussian blur for noise reduction
    fn gaussian_blur_image(img: &ImageBuffer<Luma<u8>, Vec<u8>>, sigma: f64) -> Result<ImageBuffer<Luma<u8>, Vec<u8>>> {
        // Use imageproc for efficient gaussian blur
        let blurred = imageproc::filter::gaussian_blur_f32(img, sigma as f32);
        Ok(blurred)
    }

    /// Normalize image intensities for consistent processing
    fn normalize_image(img: &ImageBuffer<Luma<u8>, Vec<u8>>) -> ImageBuffer<Luma<u8>, Vec<u8>> {
        let (width, height) = img.dimensions();
        let mut normalized: ImageBuffer<Luma<u8>, Vec<u8>> = ImageBuffer::new(width, height);
        
        // Find min and max values
        let mut min_val = 255u8;
        let mut max_val = 0u8;
        
        for pixel in img.pixels() {
            let val = pixel[0];
            min_val = min_val.min(val);
            max_val = max_val.max(val);
        }
        
        let range = (max_val - min_val) as f32;
        if range > 0.0 {
            for (src, dst) in img.pixels().zip(normalized.pixels_mut()) {
                let normalized_val = ((src[0] - min_val) as f32 / range * 255.0) as u8;
                dst[0] = normalized_val;
            }
        } else {
            normalized = img.clone();
        }
        
        normalized
    }

    /// Apply gamma correction for optimal contrast
    fn apply_gamma_correction(img: &ImageBuffer<Luma<u8>, Vec<u8>>, gamma: f64) -> ImageBuffer<Luma<u8>, Vec<u8>> {
        let (width, height) = img.dimensions();
        let mut corrected: ImageBuffer<Luma<u8>, Vec<u8>> = ImageBuffer::new(width, height);
        
        // Precompute gamma lookup table for blazing speed 🚀
        let mut gamma_table = [0u8; 256];
        for i in 0..256 {
            let normalized = i as f64 / 255.0;
            let corrected_val = (normalized.powf(gamma) * 255.0) as u8;
            gamma_table[i] = corrected_val;
        }
        
        for (src, dst) in img.pixels().zip(corrected.pixels_mut()) {
            dst[0] = gamma_table[src[0] as usize];
        }
        
        corrected
    }

    /// Auto-align image using template matching 🚀
    pub fn auto_align_image(img: DynamicImage, template: &OmrTemplate) -> Result<DynamicImage> {
        // For now, return the original image
        // TODO: Implement sophisticated feature-based alignment using pure Rust
        // This would involve:
        // 1. Feature detection (Harris corners, ORB features)
        // 2. Feature matching using descriptors
        // 3. Homography estimation using RANSAC
        // 4. Perspective transformation
        
        Ok(img)
    }

    /// Apply advanced CLAHE (Contrast Limited Adaptive Histogram Equalization)
    pub fn apply_clahe(img: &ImageBuffer<Luma<u8>, Vec<u8>>, clip_limit: f64) -> Result<ImageBuffer<Luma<u8>, Vec<u8>>> {
        // Implement a simplified CLAHE algorithm
        let (width, height) = img.dimensions();
        let mut result = img.clone();
        
        // Tile size for CLAHE processing
        let tile_width = 8;
        let tile_height = 8;
        
        for tile_y in (0..height).step_by(tile_height) {
            for tile_x in (0..width).step_by(tile_width) {
                let end_x = (tile_x + tile_width as u32).min(width);
                let end_y = (tile_y + tile_height as u32).min(height);
                
                // Apply histogram equalization to tile
                Self::apply_histogram_equalization_to_region(&mut result, tile_x, tile_y, end_x, end_y);
            }
        }
        
        Ok(result)
    }

    /// Apply histogram equalization to a region
    fn apply_histogram_equalization_to_region(img: &mut ImageBuffer<Luma<u8>, Vec<u8>>, 
                                             start_x: u32, start_y: u32, end_x: u32, end_y: u32) {
        // Calculate histogram for the region
        let mut histogram = [0u32; 256];
        let mut pixel_count = 0;
        
        for y in start_y..end_y {
            for x in start_x..end_x {
                if let Some(pixel) = img.get_pixel_checked(x, y) {
                    histogram[pixel[0] as usize] += 1;
                    pixel_count += 1;
                }
            }
        }
        
        if pixel_count == 0 {
            return;
        }
        
        // Calculate cumulative distribution function
        let mut cdf = [0u32; 256];
        cdf[0] = histogram[0];
        for i in 1..256 {
            cdf[i] = cdf[i - 1] + histogram[i];
        }
        
        // Apply histogram equalization
        for y in start_y..end_y {
            for x in start_x..end_x {
                if let Some(pixel) = img.get_pixel_mut_checked(x, y) {
                    let old_val = pixel[0] as usize;
                    let new_val = ((cdf[old_val] as f64 / pixel_count as f64) * 255.0) as u8;
                    pixel[0] = new_val;
                }
            }
        }
    }

    /// Apply morphological operations for cleaning
    pub fn apply_morphology(img: &ImageBuffer<Luma<u8>, Vec<u8>>, operation: &str) -> Result<ImageBuffer<Luma<u8>, Vec<u8>>> {
        match operation {
            "erode" => Ok(Self::morphological_erode(img, 3)),
            "dilate" => Ok(Self::morphological_dilate(img, 3)),
            "open" => {
                let eroded = Self::morphological_erode(img, 3);
                Ok(Self::morphological_dilate(&eroded, 3))
            },
            "close" => {
                let dilated = Self::morphological_dilate(img, 3);
                Ok(Self::morphological_erode(&dilated, 3))
            },
            _ => Ok(img.clone()),
        }
    }

    /// Morphological erosion
    fn morphological_erode(img: &ImageBuffer<Luma<u8>, Vec<u8>>, kernel_size: u32) -> ImageBuffer<Luma<u8>, Vec<u8>> {
        let (width, height) = img.dimensions();
        let mut result = ImageBuffer::new(width, height);
        let radius = kernel_size / 2;
        
        for y in 0..height {
            for x in 0..width {
                let mut min_val = 255u8;
                
                for ky in y.saturating_sub(radius)..=(y + radius).min(height - 1) {
                    for kx in x.saturating_sub(radius)..=(x + radius).min(width - 1) {
                        if let Some(pixel) = img.get_pixel_checked(kx, ky) {
                            min_val = min_val.min(pixel[0]);
                        }
                    }
                }
                
                result.put_pixel(x, y, Luma([min_val]));
            }
        }
        
        result
    }

    /// Morphological dilation
    fn morphological_dilate(img: &ImageBuffer<Luma<u8>, Vec<u8>>, kernel_size: u32) -> ImageBuffer<Luma<u8>, Vec<u8>> {
        let (width, height) = img.dimensions();
        let mut result = ImageBuffer::new(width, height);
        let radius = kernel_size / 2;
        
        for y in 0..height {
            for x in 0..width {
                let mut max_val = 0u8;
                
                for ky in y.saturating_sub(radius)..=(y + radius).min(height - 1) {
                    for kx in x.saturating_sub(radius)..=(x + radius).min(width - 1) {
                        if let Some(pixel) = img.get_pixel_checked(kx, ky) {
                            max_val = max_val.max(pixel[0]);
                        }
                    }
                }
                
                result.put_pixel(x, y, Luma([max_val]));
            }
        }
        
        result
    }

    /// Detect edges using Sobel edge detection
    pub fn detect_edges(img: &ImageBuffer<Luma<u8>, Vec<u8>>, threshold: f64) -> Result<ImageBuffer<Luma<u8>, Vec<u8>>> {
        // Use imageproc's Sobel gradients
        use imageproc::gradients::sobel_gradients;
        let edges = sobel_gradients(img);
        
        // Convert gradient magnitudes to binary edge image
        let (width, height) = img.dimensions();
        let mut edge_img: ImageBuffer<Luma<u8>, Vec<u8>> = ImageBuffer::new(width, height);
        
        for (gradient, edge_pixel) in edges.pixels().zip(edge_img.pixels_mut()) {
            let magnitude = ((gradient[0] as f64).powi(2) + (gradient[1] as f64).powi(2)).sqrt();
            edge_pixel[0] = if magnitude > threshold { 255 } else { 0 };
        }
        
        Ok(edge_img)
    }

    /// Apply threshold to create binary image
    pub fn apply_threshold(img: &ImageBuffer<Luma<u8>, Vec<u8>>, threshold: u8) -> ImageBuffer<Luma<u8>, Vec<u8>> {
        let (width, height) = img.dimensions();
        let mut binary: ImageBuffer<Luma<u8>, Vec<u8>> = ImageBuffer::new(width, height);
        
        for (src, dst) in img.pixels().zip(binary.pixels_mut()) {
            dst[0] = if src[0] < threshold { 0 } else { 255 };
        }
        
        binary
    }

    /// Apply median filter for noise reduction
    pub fn apply_median_filter(img: &ImageBuffer<Luma<u8>, Vec<u8>>, radius: u32) -> ImageBuffer<Luma<u8>, Vec<u8>> {
        let (width, height) = img.dimensions();
        let mut result = ImageBuffer::new(width, height);
        
        for y in 0..height {
            for x in 0..width {
                let mut neighborhood = Vec::new();
                
                for ky in y.saturating_sub(radius)..=(y + radius).min(height - 1) {
                    for kx in x.saturating_sub(radius)..=(x + radius).min(width - 1) {
                        if let Some(pixel) = img.get_pixel_checked(kx, ky) {
                            neighborhood.push(pixel[0]);
                        }
                    }
                }
                
                neighborhood.sort_unstable();
                let median = neighborhood[neighborhood.len() / 2];
                result.put_pixel(x, y, Luma([median]));
            }
        }
        
        result
    }
}