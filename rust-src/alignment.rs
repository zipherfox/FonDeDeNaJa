// alignment.rs - 🚀 Blazingly Fast Image Alignment with Memory Safety 🚀

use anyhow::{Context, Result};
use image::{DynamicImage, ImageBuffer, Luma};
use nalgebra::{DMatrix, Matrix3};
use std::collections::HashMap;

use crate::template::OmrTemplate;

/// 🚀 Blazingly Fast Image Alignment Engine 🚀
pub struct AlignmentEngine {
    // Feature detection parameters
    feature_threshold: f64,
    max_features: usize,
}

impl AlignmentEngine {
    /// Create new alignment engine with optimized parameters
    pub fn new() -> Result<Self> {
        Ok(Self {
            feature_threshold: 0.01,
            max_features: 500,
        })
    }

    /// Align image to template with 🚀 Memory Safety 🚀
    pub fn align_image_to_template(&self, image: &DynamicImage, template: &OmrTemplate) -> Result<DynamicImage> {
        // For now, implement a simplified alignment
        // In a full implementation, this would:
        // 1. Detect features in both image and template
        // 2. Match features using descriptors
        // 3. Estimate homography using RANSAC
        // 4. Apply perspective transformation
        
        Ok(image.clone())
    }

    /// Detect Harris corners for feature matching
    pub fn detect_harris_corners(&self, image: &ImageBuffer<Luma<u8>, Vec<u8>>) -> Result<Vec<(u32, u32, f64)>> {
        let (width, height) = image.dimensions();
        let mut corners = Vec::new();
        
        // Harris corner detection parameters
        let window_size = 3;
        let k = 0.04;
        
        // Calculate gradients
        let (grad_x, grad_y) = self.calculate_gradients(image)?;
        
        // Calculate Harris response
        for y in window_size..height - window_size {
            for x in window_size..width - window_size {
                let harris_response = self.calculate_harris_response(&grad_x, &grad_y, x, y, window_size, k)?;
                
                if harris_response > self.feature_threshold {
                    corners.push((x, y, harris_response));
                }
            }
        }
        
        // Sort by response strength and keep only the best features
        corners.sort_by(|a, b| b.2.partial_cmp(&a.2).unwrap());
        corners.truncate(self.max_features);
        
        Ok(corners)
    }

    /// Calculate image gradients using Sobel operators
    fn calculate_gradients(&self, image: &ImageBuffer<Luma<u8>, Vec<u8>>) -> Result<(ImageBuffer<Luma<i16>, Vec<i16>>, ImageBuffer<Luma<i16>, Vec<i16>>)> {
        let (width, height) = image.dimensions();
        let mut grad_x = ImageBuffer::new(width, height);
        let mut grad_y = ImageBuffer::new(width, height);
        
        // Sobel X kernel: [-1, 0, 1; -2, 0, 2; -1, 0, 1]
        // Sobel Y kernel: [-1, -2, -1; 0, 0, 0; 1, 2, 1]
        
        for y in 1..height - 1 {
            for x in 1..width - 1 {
                let mut gx = 0i16;
                let mut gy = 0i16;
                
                // Apply Sobel X
                gx += -1 * image.get_pixel(x - 1, y - 1)[0] as i16;
                gx += -2 * image.get_pixel(x - 1, y)[0] as i16;
                gx += -1 * image.get_pixel(x - 1, y + 1)[0] as i16;
                gx += 1 * image.get_pixel(x + 1, y - 1)[0] as i16;
                gx += 2 * image.get_pixel(x + 1, y)[0] as i16;
                gx += 1 * image.get_pixel(x + 1, y + 1)[0] as i16;
                
                // Apply Sobel Y
                gy += -1 * image.get_pixel(x - 1, y - 1)[0] as i16;
                gy += -2 * image.get_pixel(x, y - 1)[0] as i16;
                gy += -1 * image.get_pixel(x + 1, y - 1)[0] as i16;
                gy += 1 * image.get_pixel(x - 1, y + 1)[0] as i16;
                gy += 2 * image.get_pixel(x, y + 1)[0] as i16;
                gy += 1 * image.get_pixel(x + 1, y + 1)[0] as i16;
                
                grad_x.put_pixel(x, y, Luma([gx]));
                grad_y.put_pixel(x, y, Luma([gy]));
            }
        }
        
        Ok((grad_x, grad_y))
    }

    /// Calculate Harris corner response
    fn calculate_harris_response(&self, grad_x: &ImageBuffer<Luma<i16>, Vec<i16>>, 
                                grad_y: &ImageBuffer<Luma<i16>, Vec<i16>>, 
                                x: u32, y: u32, window_size: u32, k: f64) -> Result<f64> {
        
        let mut ixx = 0.0;
        let mut iyy = 0.0;
        let mut ixy = 0.0;
        
        let half_window = window_size / 2;
        
        for wy in y - half_window..=y + half_window {
            for wx in x - half_window..=x + half_window {
                let gx = grad_x.get_pixel(wx, wy)[0] as f64;
                let gy = grad_y.get_pixel(wx, wy)[0] as f64;
                
                ixx += gx * gx;
                iyy += gy * gy;
                ixy += gx * gy;
            }
        }
        
        // Harris response: det(M) - k * trace(M)^2
        // where M = [[Ixx, Ixy], [Ixy, Iyy]]
        let det = ixx * iyy - ixy * ixy;
        let trace = ixx + iyy;
        let response = det - k * trace * trace;
        
        Ok(response)
    }

    /// Perform auto-alignment using edge detection
    pub fn auto_align_using_edges(&self, image: &DynamicImage) -> Result<DynamicImage> {
        // Convert to grayscale
        let gray_img = image.to_luma8();
        
        // Detect page boundaries and corners
        let corners = self.detect_page_corners(&gray_img)?;
        
        // Apply perspective correction if corners found
        if corners.len() == 4 {
            self.correct_perspective(&gray_img, &corners)
        } else {
            Ok(image.clone())
        }
    }

    /// Detect page corners for perspective correction
    fn detect_page_corners(&self, image: &ImageBuffer<Luma<u8>, Vec<u8>>) -> Result<Vec<(f32, f32)>> {
        // Simplified corner detection using contour analysis
        let binary = self.detect_page_edges(image)?;
        let contours = self.find_contours(&binary)?;
        
        // Find the largest rectangular contour (assumed to be the page)
        if let Some(page_contour) = self.find_largest_rectangular_contour(&contours) {
            Ok(page_contour)
        } else {
            // Fallback to image corners
            let (width, height) = image.dimensions();
            Ok(vec![
                (0.0, 0.0),
                (width as f32, 0.0),
                (width as f32, height as f32),
                (0.0, height as f32),
            ])
        }
    }

    /// Detect page edges using edge detection
    fn detect_page_edges(&self, image: &ImageBuffer<Luma<u8>, Vec<u8>>) -> Result<ImageBuffer<Luma<u8>, Vec<u8>>> {
        // Apply Gaussian blur first
        let blurred = imageproc::filter::gaussian_blur_f32(image, 1.0);
        
        // Apply Sobel edge detection
        use imageproc::gradients::sobel_gradients;
        let edges = sobel_gradients(&blurred);
        
        // Convert to binary image
        let (width, height) = image.dimensions();
        let mut binary: ImageBuffer<Luma<u8>, Vec<u8>> = ImageBuffer::new(width, height);
        
        for (gradient, binary_pixel) in edges.pixels().zip(binary.pixels_mut()) {
            let magnitude = ((gradient[0] as f64).powi(2) + (gradient[1] as f64).powi(2)).sqrt();
            binary_pixel[0] = if magnitude > 50.0 { 255 } else { 0 };
        }
        
        Ok(binary)
    }

    /// Find contours in binary image
    fn find_contours(&self, binary: &ImageBuffer<Luma<u8>, Vec<u8>>) -> Result<Vec<Vec<(u32, u32)>>> {
        // Simplified contour detection
        let mut contours = Vec::new();
        let (width, height) = binary.dimensions();
        let mut visited = vec![vec![false; width as usize]; height as usize];
        
        for y in 0..height {
            for x in 0..width {
                if binary.get_pixel(x, y)[0] == 255 && !visited[y as usize][x as usize] {
                    let contour = self.trace_contour(binary, &mut visited, x, y)?;
                    if contour.len() > 50 {  // Filter small contours
                        contours.push(contour);
                    }
                }
            }
        }
        
        Ok(contours)
    }

    /// Trace a single contour
    fn trace_contour(&self, binary: &ImageBuffer<Luma<u8>, Vec<u8>>, 
                     visited: &mut Vec<Vec<bool>>, start_x: u32, start_y: u32) -> Result<Vec<(u32, u32)>> {
        let mut contour = Vec::new();
        let mut stack = vec![(start_x, start_y)];
        let (width, height) = binary.dimensions();
        
        while let Some((x, y)) = stack.pop() {
            if visited[y as usize][x as usize] {
                continue;
            }
            
            visited[y as usize][x as usize] = true;
            contour.push((x, y));
            
            // Check 8-connected neighbors
            for dy in -1i32..=1 {
                for dx in -1i32..=1 {
                    if dx == 0 && dy == 0 {
                        continue;
                    }
                    
                    let nx = x as i32 + dx;
                    let ny = y as i32 + dy;
                    
                    if nx >= 0 && nx < width as i32 && ny >= 0 && ny < height as i32 {
                        let nx = nx as u32;
                        let ny = ny as u32;
                        
                        if binary.get_pixel(nx, ny)[0] == 255 && !visited[ny as usize][nx as usize] {
                            stack.push((nx, ny));
                        }
                    }
                }
            }
        }
        
        Ok(contour)
    }

    /// Find the largest rectangular contour
    fn find_largest_rectangular_contour(&self, contours: &[Vec<(u32, u32)>]) -> Option<Vec<(f32, f32)>> {
        let mut best_contour = None;
        let mut best_area = 0.0;
        
        for contour in contours {
            if let Some(corners) = self.approximate_rectangle(contour) {
                let area = self.calculate_quadrilateral_area(&corners);
                if area > best_area {
                    best_area = area;
                    best_contour = Some(corners);
                }
            }
        }
        
        best_contour
    }

    /// Approximate contour as rectangle
    fn approximate_rectangle(&self, contour: &[(u32, u32)]) -> Option<Vec<(f32, f32)>> {
        if contour.len() < 4 {
            return None;
        }
        
        // Find bounding box corners
        let min_x = contour.iter().map(|p| p.0).min().unwrap() as f32;
        let max_x = contour.iter().map(|p| p.0).max().unwrap() as f32;
        let min_y = contour.iter().map(|p| p.1).min().unwrap() as f32;
        let max_y = contour.iter().map(|p| p.1).max().unwrap() as f32;
        
        // Return rectangle corners
        Some(vec![
            (min_x, min_y),
            (max_x, min_y),
            (max_x, max_y),
            (min_x, max_y),
        ])
    }

    /// Calculate area of quadrilateral
    fn calculate_quadrilateral_area(&self, corners: &[(f32, f32)]) -> f32 {
        if corners.len() != 4 {
            return 0.0;
        }
        
        // Use shoelace formula
        let mut area = 0.0;
        for i in 0..4 {
            let j = (i + 1) % 4;
            area += corners[i].0 * corners[j].1;
            area -= corners[j].0 * corners[i].1;
        }
        
        area.abs() / 2.0
    }

    /// Correct perspective distortion
    fn correct_perspective(&self, image: &ImageBuffer<Luma<u8>, Vec<u8>>, corners: &[(f32, f32)]) -> Result<DynamicImage> {
        // For now, return original image
        // Full implementation would apply perspective transformation using homography
        Ok(DynamicImage::ImageLuma8(image.clone()))
    }

    /// Perform template-based alignment using cross-correlation
    pub fn template_alignment(&self, image: &DynamicImage, template_regions: &[(u32, u32, u32, u32)]) -> Result<(i32, i32)> {
        // Template matching for alignment offset detection
        let gray_img = image.to_luma8();
        
        // For each template region, find best match in image
        let mut best_offset = (0i32, 0i32);
        
        for &(template_x, template_y, template_w, template_h) in template_regions {
            // Extract template region (simplified)
            if let Some(offset) = self.find_template_match(&gray_img, template_x, template_y, template_w, template_h)? {
                // For simplicity, use first good match
                best_offset = offset;
                break;
            }
        }

        Ok(best_offset)
    }

    /// Find template match using normalized cross-correlation
    fn find_template_match(&self, image: &ImageBuffer<Luma<u8>, Vec<u8>>, 
                          template_x: u32, template_y: u32, 
                          template_w: u32, template_h: u32) -> Result<Option<(i32, i32)>> {
        
        let (img_width, img_height) = image.dimensions();
        
        // Bounds checking
        if template_x + template_w >= img_width || template_y + template_h >= img_height {
            return Ok(None);
        }

        // Extract template
        let mut template = ImageBuffer::new(template_w, template_h);
        for y in 0..template_h {
            for x in 0..template_w {
                if let Some(pixel) = image.get_pixel_checked(template_x + x, template_y + y) {
                    template.put_pixel(x, y, *pixel);
                }
            }
        }

        // Search for best match in surrounding area
        let search_radius = 50u32;
        let search_start_x = template_x.saturating_sub(search_radius);
        let search_start_y = template_y.saturating_sub(search_radius);
        let search_end_x = (template_x + search_radius).min(img_width - template_w);
        let search_end_y = (template_y + search_radius).min(img_height - template_h);

        let mut best_correlation = 0.0;
        let mut best_offset = None;

        for search_y in search_start_y..search_end_y {
            for search_x in search_start_x..search_end_x {
                let correlation = self.calculate_normalized_correlation(image, &template, search_x, search_y)?;
                
                if correlation > best_correlation && correlation > 0.8 {
                    best_correlation = correlation;
                    best_offset = Some((
                        search_x as i32 - template_x as i32,
                        search_y as i32 - template_y as i32,
                    ));
                }
            }
        }

        Ok(best_offset)
    }

    /// Calculate normalized cross-correlation
    fn calculate_normalized_correlation(&self, image: &ImageBuffer<Luma<u8>, Vec<u8>>, 
                                      template: &ImageBuffer<Luma<u8>, Vec<u8>>, 
                                      x: u32, y: u32) -> Result<f64> {
        
        let (template_w, template_h) = template.dimensions();
        let (img_width, img_height) = image.dimensions();

        if x + template_w >= img_width || y + template_h >= img_height {
            return Ok(0.0);
        }

        let mut sum_template = 0f64;
        let mut sum_image = 0f64;
        let mut sum_template_sq = 0f64;
        let mut sum_image_sq = 0f64;
        let mut sum_product = 0f64;
        let n = (template_w * template_h) as f64;

        for ty in 0..template_h {
            for tx in 0..template_w {
                let template_val = template.get_pixel(tx, ty)[0] as f64;
                let image_val = image.get_pixel(x + tx, y + ty)[0] as f64;

                sum_template += template_val;
                sum_image += image_val;
                sum_template_sq += template_val * template_val;
                sum_image_sq += image_val * image_val;
                sum_product += template_val * image_val;
            }
        }

        let mean_template = sum_template / n;
        let mean_image = sum_image / n;

        let numerator = sum_product - n * mean_template * mean_image;
        let denominator = ((sum_template_sq - n * mean_template * mean_template) *
                          (sum_image_sq - n * mean_image * mean_image)).sqrt();

        if denominator > 0.0 {
            Ok(numerator / denominator)
        } else {
            Ok(0.0)
        }
    }
}