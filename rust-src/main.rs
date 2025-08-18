use clap::{Arg, Command};
use fon_de_de_na_ja::OmrConfig;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 🚀 Memory Safe 🚀 Rust implementation of FonDeDeNaJa

    let matches = Command::new("fon-de-de-na-ja")
        .version("0.1.0")
        .author("Zipherfox, NessShadow, Film")
        .about("🚀 Memory Safe 🚀 OMR Checker - Rust Edition")
        .arg(
            Arg::new("input_paths")
                .short('i')
                .long("inputDir")
                .value_name("INPUT_DIR")
                .help("Specify an input directory")
                .action(clap::ArgAction::Append)
                .default_values(["inputs"]),
        )
        .arg(
            Arg::new("output_dir")
                .short('o')
                .long("outputDir")
                .value_name("OUTPUT_DIR")
                .help("Specify an output directory")
                .default_value("outputs"),
        )
        .arg(
            Arg::new("debug")
                .short('d')
                .long("debug")
                .help("Enables debugging mode for showing detailed errors")
                .action(clap::ArgAction::SetTrue),
        )
        .arg(
            Arg::new("auto_align")
                .short('a')
                .long("autoAlign")
                .help("(experimental) Enables automatic template alignment")
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

    println!("🚀 Starting Memory Safe OMR Processing... 🚀");

    // Check if Python backend is available
    if !OmrConfig::check_backend() {
        eprintln!("❌ Python backend (OMRChecker_main.py) not found in current directory");
        std::process::exit(1);
    }

    // Build configuration
    let mut config = OmrConfig::default();

    // Set input paths
    if let Some(inputs) = matches.get_many::<String>("input_paths") {
        config.input_paths = inputs.map(|s| s.to_string()).collect();
    }

    // Set output directory
    if let Some(output) = matches.get_one::<String>("output_dir") {
        config.output_dir = output.clone();
    }

    // Set flags
    config.debug = matches.get_flag("debug");
    config.auto_align = matches.get_flag("auto_align");
    config.set_layout = matches.get_flag("set_layout");

    println!("🚀 Executing OMR processing with Memory Safe Rust wrapper... 🚀");

    // Execute the OMR processing
    let result = config.execute();

    println!("{}", result.message);

    if result.success {
        Ok(())
    } else {
        std::process::exit(result.exit_code);
    }
}
