use anyhow::Result;
use clap::{Arg, Command};
use fon_de_de_na_ja::OmrConfig;
use std::path::PathBuf;

fn main() -> Result<()> {
    // 🚀 Blazingly Fast Memory Safe 🚀 Rust implementation of FonDeDeNaJa

    let matches = Command::new("fon-de-de-na-ja")
        .version("0.1.0")
        .author("Zipherfox, NessShadow, Film")
        .about("🚀 Blazingly Fast Memory Safe OMR Checker - Complete Rust Edition 🚀")
        .arg(
            Arg::new("input_paths")
                .short('i')
                .long("inputDir")
                .value_name("INPUT_DIR")
                .help("Specify input directories or files")
                .action(clap::ArgAction::Append)
                .default_values(["inputs"]),
        )
        .arg(
            Arg::new("output_dir")
                .short('o')
                .long("outputDir")
                .value_name("OUTPUT_DIR")
                .help("Specify output directory")
                .default_value("outputs"),
        )
        .arg(
            Arg::new("template")
                .short('t')
                .long("template")
                .value_name("TEMPLATE_FILE")
                .help("Specify template JSON file"),
        )
        .arg(
            Arg::new("debug")
                .short('d')
                .long("debug")
                .help("Enable debugging mode for detailed output")
                .action(clap::ArgAction::SetTrue),
        )
        .arg(
            Arg::new("auto_align")
                .short('a')
                .long("autoAlign")
                .help("Enable automatic template alignment")
                .action(clap::ArgAction::SetTrue),
        )
        .arg(
            Arg::new("set_layout")
                .short('l')
                .long("setLayout")
                .help("Set up OMR template layout")
                .action(clap::ArgAction::SetTrue),
        )
        .get_matches();

    println!("🚀 Starting Blazingly Fast Memory Safe OMR Processing... 🚀");

    // Build configuration
    let mut config = OmrConfig::default();

    // Set input paths
    if let Some(inputs) = matches.get_many::<String>("input_paths") {
        config.input_paths = inputs.map(|s| PathBuf::from(s)).collect();
    }

    // Set output directory
    if let Some(output) = matches.get_one::<String>("output_dir") {
        config.output_dir = PathBuf::from(output);
    }

    // Set template path
    if let Some(template) = matches.get_one::<String>("template") {
        config.template_path = Some(PathBuf::from(template));
    }

    // Set flags
    config.debug = matches.get_flag("debug");
    config.auto_align = matches.get_flag("auto_align");
    config.set_layout = matches.get_flag("set_layout");

    // Display configuration if debug mode
    if config.debug {
        println!("🚀 Configuration:");
        println!("  Input paths: {:?}", config.input_paths);
        println!("  Output directory: {:?}", config.output_dir);
        println!("  Template: {:?}", config.template_path);
        println!("  Auto-align: {}", config.auto_align);
        println!("  Debug mode: {}", config.debug);
    }

    println!("🚀 Executing blazingly fast OMR processing with complete Rust implementation... 🚀");

    // Execute the OMR processing
    let result = config.execute()?;

    println!("{}", result.message);
    
    if config.debug {
        println!("🚀 Processing statistics:");
        println!("  Files processed: {}", result.processed_files.len());
        println!("  Total time: {:.2} seconds", result.total_processing_time);
        
        if !result.errors.is_empty() {
            println!("  Errors encountered:");
            for error in &result.errors {
                println!("    - {}", error);
            }
        }
        
        // Show per-file statistics
        for file in &result.processed_files {
            println!("  📄 {}: {} bubbles detected, confidence: {:.2}%, time: {:.3}s", 
                    file.file_path.display(),
                    file.detected_bubbles.len(),
                    file.confidence_score * 100.0,
                    file.processing_time);
        }
    }

    if result.success {
        println!("🚀 All processing completed successfully with blazing speed and memory safety! 🚀");
        Ok(())
    } else {
        eprintln!("❌ OMR processing encountered errors");
        std::process::exit(1);
    }
}
