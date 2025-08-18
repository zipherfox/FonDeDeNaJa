// web_main.rs - 🚀 Blazingly Fast Memory Safe OMR Web Interface 🚀
//! Web interface for the FonDeDeNaJa OMR processing system
//! 
//! Provides a modern web UI similar to Streamlit but with blazing fast Rust performance

use anyhow::Result;
use axum::{
    body::Body,
    extract::{Multipart, Query, State},
    http::{header, StatusCode},
    response::{Html, IntoResponse, Json, Response},
    routing::{get, post},
    Router,
};
use fon_de_de_na_ja::{OmrConfig, OmrResult};
use serde::{Deserialize, Serialize};
use std::{
    collections::HashMap,
    path::PathBuf,
    sync::{Arc, Mutex},
    time::SystemTime,
};
use tokio::fs;
use tower::ServiceBuilder;
use tower_http::{
    cors::CorsLayer,
    services::ServeDir,
    trace::TraceLayer,
};
use tracing::{info, warn};
use uuid::Uuid;

// 🚀 Application state for blazingly fast processing 🚀
#[derive(Clone)]
struct AppState {
    jobs: Arc<Mutex<HashMap<String, ProcessingJob>>>,
}

// Processing job status
#[derive(Debug, Clone, Serialize)]
struct ProcessingJob {
    id: String,
    status: JobStatus,
    created_at: SystemTime,
    result: Option<OmrResult>,
    error: Option<String>,
    config: OmrConfig,
}

#[derive(Debug, Clone, Serialize)]
enum JobStatus {
    Pending,
    Processing,
    Completed,
    Failed,
}

// API request/response types
#[derive(Deserialize)]
struct ProcessingRequest {
    auto_align: Option<bool>,
    debug: Option<bool>,
}

#[derive(Serialize)]
struct ProcessingResponse {
    job_id: String,
    status: String,
    message: String,
}

#[derive(Serialize)]
struct JobStatusResponse {
    job_id: String,
    status: JobStatus,
    progress: Option<String>,
    result: Option<OmrResult>,
    error: Option<String>,
}

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize blazingly fast tracing 🚀
    tracing_subscriber::fmt()
        .with_env_filter("fon_de_de_na_ja=info,tower_http=debug")
        .init();

    info!("🚀 Starting Blazingly Fast Memory Safe OMR Web Interface... 🚀");

    // Create application state
    let state = AppState {
        jobs: Arc::new(Mutex::new(HashMap::new())),
    };

    // Create temp directory for uploads
    let upload_dir = PathBuf::from("web_uploads");
    fs::create_dir_all(&upload_dir).await?;

    // Create static directory for web assets
    let static_dir = PathBuf::from("web_static");
    fs::create_dir_all(&static_dir).await?;
    
    // Create the web interface HTML if it doesn't exist
    create_web_assets(&static_dir).await?;

    // Build router with blazingly fast routes 🚀
    let app = Router::new()
        .route("/", get(serve_index))
        .route("/upload", post(upload_files))
        .route("/process", post(start_processing))
        .route("/status/:job_id", get(get_job_status))
        .route("/api/health", get(health_check))
        .nest_service("/static", ServeDir::new(&static_dir))
        .layer(
            ServiceBuilder::new()
                .layer(TraceLayer::new_for_http())
                .layer(CorsLayer::permissive()),
        )
        .with_state(state);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await?;
    
    info!("🚀 Web interface running at http://0.0.0.0:3000 🚀");
    info!("🚀 Upload your OMR sheets and experience blazing fast processing! 🚀");

    axum::serve(listener, app).await?;

    Ok(())
}

// Serve the main web interface
async fn serve_index() -> impl IntoResponse {
    let html_content = r#"<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 FonDeDeNaJa - Blazingly Fast OMR Processing 🚀</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .header p {
            font-size: 1.2em;
            color: #666;
        }
        
        .upload-section {
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            margin-bottom: 30px;
        }
        
        .upload-zone {
            border: 3px dashed #667eea;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            background: #f8f9ff;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .upload-zone:hover {
            border-color: #764ba2;
            background: #f0f2ff;
        }
        
        .upload-zone.dragover {
            border-color: #764ba2;
            background: #e8ebff;
        }
        
        .btn {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: transform 0.2s ease;
        }
        
        .btn:hover {
            transform: translateY(-2px);
        }
        
        .options {
            display: flex;
            gap: 20px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        
        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .results-section {
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            display: none;
        }
        
        .status {
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            font-weight: bold;
        }
        
        .status.pending { background: #fff3cd; color: #856404; }
        .status.processing { background: #cce7ff; color: #0056b3; }
        .status.completed { background: #d4edda; color: #155724; }
        .status.failed { background: #f8d7da; color: #721c24; }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .file-list {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }
        
        .file-item {
            padding: 8px;
            border-bottom: 1px solid #dee2e6;
        }
        
        .file-item:last-child {
            border-bottom: none;
        }
        
        .download-btn {
            background: #28a745;
            margin-top: 15px;
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 FonDeDeNaJa OMR Processor 🚀</h1>
            <p>Blazingly Fast Memory Safe Optical Mark Recognition with Rust</p>
        </div>
        
        <div class="upload-section">
            <h2>Upload OMR Sheets</h2>
            <div class="upload-zone" id="uploadZone">
                <p>📁 Drop your OMR image files here or click to browse</p>
                <p><small>Supported formats: JPG, JPEG, PNG, BMP, TIFF</small></p>
                <input type="file" id="fileInput" multiple accept="image/*" style="display: none;">
            </div>
            
            <div class="options">
                <div class="checkbox-group">
                    <input type="checkbox" id="autoAlign">
                    <label for="autoAlign">🎯 Auto-align images</label>
                </div>
                <div class="checkbox-group">
                    <input type="checkbox" id="debug">
                    <label for="debug">🔍 Debug mode</label>
                </div>
            </div>
            
            <div id="fileList" class="file-list" style="display: none;">
                <h3>Selected Files:</h3>
                <div id="files"></div>
            </div>
            
            <button class="btn" id="processBtn" style="display: none;">
                🚀 Start Processing with Blazing Speed 🚀
            </button>
        </div>
        
        <div class="results-section" id="resultsSection">
            <h2>Processing Results</h2>
            <div id="status" class="status"></div>
            <div id="spinner" class="spinner" style="display: none;"></div>
            <div id="results"></div>
        </div>
    </div>

    <script>
        let uploadId = null;
        let jobId = null;
        let selectedFiles = [];
        
        const uploadZone = document.getElementById('uploadZone');
        const fileInput = document.getElementById('fileInput');
        const fileList = document.getElementById('fileList');
        const processBtn = document.getElementById('processBtn');
        const resultsSection = document.getElementById('resultsSection');
        const status = document.getElementById('status');
        const spinner = document.getElementById('spinner');
        const results = document.getElementById('results');
        
        // File upload handling
        uploadZone.addEventListener('click', () => fileInput.click());
        
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        });
        
        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('dragover');
        });
        
        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
            handleFiles(e.dataTransfer.files);
        });
        
        fileInput.addEventListener('change', (e) => {
            handleFiles(e.target.files);
        });
        
        function handleFiles(files) {
            selectedFiles = Array.from(files);
            displayFileList();
            uploadFiles();
        }
        
        function displayFileList() {
            const filesDiv = document.getElementById('files');
            filesDiv.innerHTML = '';
            
            selectedFiles.forEach(file => {
                const fileDiv = document.createElement('div');
                fileDiv.className = 'file-item';
                fileDiv.innerHTML = `📄 ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
                filesDiv.appendChild(fileDiv);
            });
            
            fileList.style.display = selectedFiles.length > 0 ? 'block' : 'none';
        }
        
        async function uploadFiles() {
            if (selectedFiles.length === 0) return;
            
            const formData = new FormData();
            selectedFiles.forEach(file => {
                formData.append('files', file);
            });
            
            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    uploadId = result.upload_id;
                    processBtn.style.display = 'block';
                    updateStatus('Ready to process! 🚀', 'pending');
                } else {
                    throw new Error(result.message || 'Upload failed');
                }
            } catch (error) {
                showError('Upload failed: ' + error.message);
            }
        }
        
        processBtn.addEventListener('click', async () => {
            if (!uploadId) return;
            
            const autoAlign = document.getElementById('autoAlign').checked;
            const debug = document.getElementById('debug').checked;
            
            try {
                const response = await fetch(`/process?upload_id=${uploadId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        auto_align: autoAlign,
                        debug: debug
                    })
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    jobId = result.job_id;
                    resultsSection.style.display = 'block';
                    processBtn.style.display = 'none';
                    pollJobStatus();
                } else {
                    throw new Error(result.message || 'Processing failed to start');
                }
            } catch (error) {
                showError('Failed to start processing: ' + error.message);
            }
        });
        
        async function pollJobStatus() {
            if (!jobId) return;
            
            try {
                const response = await fetch(`/status/${jobId}`);
                const result = await response.json();
                
                if (response.ok) {
                    updateJobStatus(result);
                    
                    if (result.status === 'Processing' || result.status === 'Pending') {
                        setTimeout(pollJobStatus, 2000);
                    }
                } else {
                    throw new Error('Failed to get job status');
                }
            } catch (error) {
                showError('Status check failed: ' + error.message);
            }
        }
        
        function updateJobStatus(jobResult) {
            const statusClass = jobResult.status.toLowerCase();
            
            switch (jobResult.status) {
                case 'Pending':
                    updateStatus('⏳ Processing queued...', statusClass);
                    spinner.style.display = 'block';
                    break;
                case 'Processing':
                    updateStatus('🚀 Processing with blazing speed...', statusClass);
                    spinner.style.display = 'block';
                    break;
                case 'Completed':
                    updateStatus('✅ Processing completed successfully!', statusClass);
                    spinner.style.display = 'none';
                    displayResults(jobResult.result);
                    break;
                case 'Failed':
                    updateStatus('❌ Processing failed', statusClass);
                    spinner.style.display = 'none';
                    if (jobResult.error) {
                        showError(jobResult.error);
                    }
                    break;
            }
        }
        
        function updateStatus(message, className) {
            status.textContent = message;
            status.className = `status ${className}`;
        }
        
        function displayResults(result) {
            if (!result) return;
            
            results.innerHTML = `
                <h3>📊 Processing Summary</h3>
                <div class="file-list">
                    <p><strong>Files processed:</strong> ${result.processed_files.length}</p>
                    <p><strong>Total time:</strong> ${result.total_processing_time.toFixed(2)} seconds</p>
                    <p><strong>Success:</strong> ${result.success ? '✅ Yes' : '❌ No'}</p>
                </div>
                
                <h3>📄 File Details</h3>
                <div class="file-list">
                    ${result.processed_files.map(file => `
                        <div class="file-item">
                            <strong>${file.file_path.split('/').pop()}</strong><br>
                            Bubbles detected: ${file.detected_bubbles.length}<br>
                            Confidence: ${(file.confidence_score * 100).toFixed(1)}%<br>
                            Processing time: ${file.processing_time.toFixed(3)}s
                        </div>
                    `).join('')}
                </div>
            `;
        }
        
        function showError(message) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error';
            errorDiv.textContent = message;
            resultsSection.appendChild(errorDiv);
            
            setTimeout(() => {
                errorDiv.remove();
            }, 5000);
        }
        
        // 🚀 Add some blazing animations 🚀
        document.addEventListener('DOMContentLoaded', () => {
            const rockets = document.querySelectorAll('h1');
            rockets.forEach(rocket => {
                rocket.addEventListener('mouseenter', () => {
                    rocket.style.transform = 'scale(1.05)';
                });
                rocket.addEventListener('mouseleave', () => {
                    rocket.style.transform = 'scale(1)';
                });
            });
        });
    </script>
</body>
</html>"#;
    
    Html(html_content)
}

// Health check endpoint
async fn health_check() -> impl IntoResponse {
    Json(serde_json::json!({
        "status": "🚀 Blazingly Fast and Memory Safe! 🚀",
        "version": "0.1.0"
    }))
}

// Handle file uploads with blazing speed 🚀
async fn upload_files(mut multipart: Multipart) -> impl IntoResponse {
    let upload_id = Uuid::new_v4().to_string();
    let upload_dir = PathBuf::from("web_uploads").join(&upload_id);
    
    if let Err(e) = fs::create_dir_all(&upload_dir).await {
        warn!("Failed to create upload directory: {}", e);
        return StatusCode::INTERNAL_SERVER_ERROR.into_response();
    }

    let mut uploaded_files = Vec::new();

    while let Some(field) = multipart.next_field().await.unwrap_or(None) {
        if let Some(file_name) = field.file_name() {
            let file_name = file_name.to_string();
            let file_path = upload_dir.join(&file_name);
            
            if let Ok(data) = field.bytes().await {
                if let Err(e) = fs::write(&file_path, &data).await {
                    warn!("Failed to save uploaded file: {}", e);
                    continue;
                }
                uploaded_files.push(file_name.clone());
                info!("🚀 Uploaded file: {} ({} bytes)", file_name, data.len());
            }
        }
    }

    if uploaded_files.is_empty() {
        return (StatusCode::BAD_REQUEST, "No files uploaded").into_response();
    }

    Json(serde_json::json!({
        "upload_id": upload_id,
        "files": uploaded_files,
        "message": "🚀 Files uploaded successfully with blazing speed! 🚀"
    })).into_response()
}

// Start OMR processing with memory safety 🚀
async fn start_processing(
    State(state): State<AppState>,
    Query(params): Query<HashMap<String, String>>,
    Json(request): Json<ProcessingRequest>,
) -> impl IntoResponse {
    let upload_id = match params.get("upload_id") {
        Some(id) => id.clone(),
        None => return (StatusCode::BAD_REQUEST, "Missing upload_id").into_response(),
    };

    let upload_dir = PathBuf::from("web_uploads").join(&upload_id);
    if !upload_dir.exists() {
        return (StatusCode::NOT_FOUND, "Upload not found").into_response();
    }

    // Create job configuration
    let mut config = OmrConfig::default();
    config.input_paths = vec![upload_dir];
    config.output_dir = PathBuf::from("web_results").join(&upload_id);
    config.auto_align = request.auto_align.unwrap_or(false);
    config.debug = request.debug.unwrap_or(false);

    // Create processing job
    let job_id = Uuid::new_v4().to_string();
    let job = ProcessingJob {
        id: job_id.clone(),
        status: JobStatus::Pending,
        created_at: SystemTime::now(),
        result: None,
        error: None,
        config: config.clone(),
    };

    // Add job to state
    {
        let mut jobs = state.jobs.lock().unwrap();
        jobs.insert(job_id.clone(), job);
    }

    // Start processing in background task
    let state_clone = state.clone();
    let job_id_clone = job_id.clone();
    tokio::spawn(async move {
        process_omr_job(state_clone, job_id_clone, config).await;
    });

    Json(ProcessingResponse {
        job_id,
        status: "pending".to_string(),
        message: "🚀 OMR processing started with blazing speed! 🚀".to_string(),
    }).into_response()
}

// Get job status with real-time updates
async fn get_job_status(
    axum::extract::Path(job_id): axum::extract::Path<String>,
    State(state): State<AppState>,
) -> impl IntoResponse {
    let jobs = state.jobs.lock().unwrap();
    
    match jobs.get(&job_id) {
        Some(job) => Json(JobStatusResponse {
            job_id: job.id.clone(),
            status: job.status.clone(),
            progress: None,
            result: job.result.clone(),
            error: job.error.clone(),
        }).into_response(),
        None => (StatusCode::NOT_FOUND, "Job not found").into_response(),
    }
}

// Background task for OMR processing
async fn process_omr_job(state: AppState, job_id: String, config: OmrConfig) {
    info!("🚀 Starting OMR processing for job: {}", job_id);

    // Update job status to processing
    {
        let mut jobs = state.jobs.lock().unwrap();
        if let Some(job) = jobs.get_mut(&job_id) {
            job.status = JobStatus::Processing;
        }
    }

    // Execute OMR processing with blazing speed 🚀
    let result = tokio::task::spawn_blocking(move || config.execute()).await;

    // Update job with results
    {
        let mut jobs = state.jobs.lock().unwrap();
        if let Some(job) = jobs.get_mut(&job_id) {
            match result {
                Ok(Ok(omr_result)) => {
                    job.status = JobStatus::Completed;
                    job.result = Some(omr_result);
                    info!("🚀 OMR processing completed successfully for job: {}", job_id);
                }
                Ok(Err(e)) => {
                    job.status = JobStatus::Failed;
                    job.error = Some(e.to_string());
                    warn!("OMR processing failed for job {}: {}", job_id, e);
                }
                Err(e) => {
                    job.status = JobStatus::Failed;
                    job.error = Some(format!("Task join error: {}", e));
                    warn!("Task failed for job {}: {}", job_id, e);
                }
            }
        }
    }
}

// Create web assets if they don't exist
async fn create_web_assets(static_dir: &PathBuf) -> Result<()> {
    // Assets are now served directly from the code for simplicity
    info!("🚀 Web assets ready for blazing fast serving! 🚀");
    Ok(())
}