use clap::{Parser, Subcommand};
use serde_json::json;

#[derive(Parser)]
#[command(name = "bukzor-color")]
#[command(about = "Color calculations and conversions CLI")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Convert colors between formats
    Convert {
        /// Input color value
        input: String,
        /// Output format (hex, rgb, hsl, hsv)
        #[arg(long, default_value = "hex")]
        to: String,
        /// Output as JSON
        #[arg(long)]
        json: bool,
    },
}

fn main() {
    let cli = Cli::parse();

    match cli.command {
        Commands::Convert { input, to, json } => {
            if json {
                let result = json!({
                    "input": input,
                    "output_format": to,
                    "result": "TODO: implement conversion"
                });
                println!("{}", serde_json::to_string_pretty(&result).unwrap());
            } else {
                println!("Converting '{}' to {}: TODO: implement", input, to);
            }
        }
    }
}
