// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::fs;
use std::path::Path;
use tauri::command;
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
struct FeedbackEntry {
    id: String,
    passage: String,
    context: String,
    feedback: String,
    timestamp: String,
    tag: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct Config {
    openai_api_key: String,
    context_file_path: String,
    theme: String,
}

#[command]
fn read_file(path: String) -> Result<String, String> {
    fs::read_to_string(&path).map_err(|e| e.to_string())
}

#[command]
fn write_file(path: String, content: String) -> Result<(), String> {
    fs::write(&path, content).map_err(|e| e.to_string())
}

#[command]
fn read_config() -> Result<Config, String> {
    let config_path = "config.json";
    if Path::new(config_path).exists() {
        let content = fs::read_to_string(config_path).map_err(|e| e.to_string())?;
        serde_json::from_str(&content).map_err(|e| e.to_string())
    } else {
        Ok(Config {
            openai_api_key: String::new(),
            context_file_path: "story_context.md".to_string(),
            theme: "light".to_string(),
        })
    }
}

#[command]
fn save_config(config: Config) -> Result<(), String> {
    let content = serde_json::to_string_pretty(&config).map_err(|e| e.to_string())?;
    fs::write("config.json", content).map_err(|e| e.to_string())
}

#[command]
fn save_feedback(feedback: FeedbackEntry) -> Result<(), String> {
    let feedback_file = "feedback.json";
    let mut feedbacks: Vec<FeedbackEntry> = if Path::new(feedback_file).exists() {
        let content = fs::read_to_string(feedback_file).map_err(|e| e.to_string())?;
        serde_json::from_str(&content).unwrap_or_default()
    } else {
        Vec::new()
    };
    
    feedbacks.push(feedback);
    let content = serde_json::to_string_pretty(&feedbacks).map_err(|e| e.to_string())?;
    fs::write(feedback_file, content).map_err(|e| e.to_string())
}

#[command]
fn load_feedback() -> Result<Vec<FeedbackEntry>, String> {
    let feedback_file = "feedback.json";
    if Path::new(feedback_file).exists() {
        let content = fs::read_to_string(feedback_file).map_err(|e| e.to_string())?;
        serde_json::from_str(&content).map_err(|e| e.to_string())
    } else {
        Ok(Vec::new())
    }
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            read_file,
            write_file,
            read_config,
            save_config,
            save_feedback,
            load_feedback
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}