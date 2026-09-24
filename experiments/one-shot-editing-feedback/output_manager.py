"""
Output management for literary analysis results.
Handles saving, loading, and formatting analysis results.
"""

import json
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import asdict
from analysis_engine import AnalysisResult


class OutputManager:
    """Manages saving and loading of analysis results."""
    
    def __init__(self, base_output_dir: str = "outputs"):
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(exist_ok=True)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for folder naming."""
        return datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
    
    def _create_output_folder(self, analysis_type: str) -> Path:
        """Create timestamped output folder."""
        folder_path = self.base_output_dir / analysis_type / self._get_timestamp()
        folder_path.mkdir(parents=True, exist_ok=True)
        return folder_path
    
    def save_chapter_analysis(self, results: Dict[int, List[AnalysisResult]], 
                             manuscript_path: str = "") -> Path:
        """Save chapter analysis results."""
        output_folder = self._create_output_folder("chapter_review")
        
        # Save metadata
        metadata = {
            "analysis_type": "chapter_review",
            "timestamp": self._get_timestamp(),
            "manuscript_path": manuscript_path,
            "chapter_count": len(results)
        }
        
        with open(output_folder / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        # Save each chapter's analysis
        for chapter_idx, chapter_results in results.items():
            self._save_chapter_file(output_folder, chapter_idx, chapter_results)
        
        return output_folder
    
    def save_holistic_analysis(self, results: List[AnalysisResult], 
                              manuscript_path: str = "") -> Path:
        """Save holistic analysis results."""
        output_folder = self._create_output_folder("holistic_review")
        
        # Save metadata
        metadata = {
            "analysis_type": "holistic_review", 
            "timestamp": self._get_timestamp(),
            "manuscript_path": manuscript_path,
            "prompt_count": len(results),
            "provider": results[0].provider if results else "unknown",
            "model": results[0].model if results else "unknown"
        }
        
        with open(output_folder / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        # Save individual prompt results
        for result in results:
            self._save_prompt_file(output_folder, result)
        
        # Save combined summary
        self._save_combined_summary(output_folder, results)
        
        return output_folder
    
    def save_multi_provider_analysis(self, multi_results: Dict[str, Any], 
                                   manuscript_path: str = "") -> Path:
        """Save multi-provider analysis results."""
        output_folder = self._create_output_folder("multi_provider_review")
        
        # Save metadata
        metadata = {
            "analysis_type": "multi_provider_review",
            "timestamp": self._get_timestamp(),
            "manuscript_path": manuscript_path,
            "providers_used": multi_results.get("providers_used", []),
            "meta_provider": multi_results.get("meta_provider", ""),
            "analysis_method": multi_results.get("analysis_type", "")
        }
        
        with open(output_folder / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        # Save each provider's results
        provider_results = multi_results.get("provider_results", {})
        for provider, results in provider_results.items():
            if isinstance(results, dict) and "error" in results:
                # Save error info
                with open(output_folder / f"{provider}_error.txt", "w") as f:
                    f.write(f"Error with {provider}: {results['error']}")
            elif isinstance(results, list):
                # Holistic analysis results
                provider_folder = output_folder / provider
                provider_folder.mkdir(exist_ok=True)
                
                for result in results:
                    self._save_prompt_file(provider_folder, result)
        
        # Save meta-analysis results
        meta_results = multi_results.get("meta_analysis", [])
        if meta_results:
            meta_folder = output_folder / "meta_analysis"
            meta_folder.mkdir(exist_ok=True)
            
            for result in meta_results:
                # Save meta-analysis with special formatting
                filename = result.prompt_name.replace("META_", "")
                with open(meta_folder / filename, "w", encoding="utf-8") as f:
                    f.write(f"# Meta-Analysis: {filename}\n\n")
                    f.write(f"**Original Prompt**: {result.prompt_text}\n\n")
                    f.write(f"**Meta-Provider**: {result.provider}\n")
                    f.write(f"**Meta-Model**: {result.model}\n\n")
                    f.write("## Synthesized Analysis\n\n")
                    f.write(result.bad_cop_response)
        
        # Save comprehensive summary
        self._save_multi_provider_summary(output_folder, multi_results)
        
        return output_folder
    
    def save_transition_analysis(self, results: Dict[str, List[AnalysisResult]], 
                                manuscript_path: str = "") -> Path:
        """Save transition analysis results."""
        output_folder = self._create_output_folder("transition_review")
        
        # Save metadata
        metadata = {
            "analysis_type": "transition_review",
            "timestamp": self._get_timestamp(), 
            "manuscript_path": manuscript_path,
            "transition_count": len(results)
        }
        
        with open(output_folder / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        # Save each transition's analysis
        for transition_key, transition_results in results.items():
            self._save_transition_file(output_folder, transition_key, transition_results)
        
        return output_folder
    
    def _save_chapter_file(self, output_folder: Path, chapter_idx: int, 
                          results: List[AnalysisResult]) -> None:
        """Save analysis for a single chapter."""
        chapter_file = output_folder / f"chapter_{chapter_idx}.md"
        
        with open(chapter_file, "w", encoding="utf-8") as f:
            f.write(f"# Chapter {chapter_idx} Analysis\n\n")
            
            for result in results:
                f.write(f"## {result.prompt_name}\n\n")
                
                if result.error:
                    f.write(f"**Error:** {result.error}\n\n")
                else:
                    f.write("### Bad Cop Analysis\n\n")
                    f.write(result.bad_cop_response)
                    f.write("\n\n### Good Cop Analysis\n\n") 
                    f.write(result.good_cop_response)
                
                f.write("\n\n---\n\n")
    
    def _save_transition_file(self, output_folder: Path, transition_key: str,
                             results: List[AnalysisResult]) -> None:
        """Save analysis for a transition."""
        transition_file = output_folder / f"{transition_key}.md"
        
        with open(transition_file, "w", encoding="utf-8") as f:
            f.write(f"# {transition_key.replace('_', ' ').title()} Analysis\n\n")
            
            for result in results:
                f.write(f"## {result.prompt_name}\n\n")
                f.write(f"### Question\n{result.prompt_text}\n\n")
                
                if result.error:
                    f.write(f"**Error:** {result.error}\n\n")
                else:
                    f.write("### Bad Cop Analysis\n\n")
                    f.write(result.bad_cop_response)
                    f.write("\n\n### Good Cop Analysis\n\n")
                    f.write(result.good_cop_response)
                
                f.write("\n\n---\n\n")
    
    def _save_prompt_file(self, output_folder: Path, result: AnalysisResult) -> None:
        """Save individual prompt result to file."""
        with open(output_folder / result.prompt_name, "w", encoding="utf-8") as f:
            if result.error:
                f.write(f"ERROR\n\n{result.error}")
            else:
                f.write("BAD COP\n\n")
                f.write(result.bad_cop_response)
                f.write("\n\nGOOD COP\n\n")
                f.write(result.good_cop_response)
    
    def _save_combined_summary(self, output_folder: Path, 
                              results: List[AnalysisResult]) -> None:
        """Save combined summary of all analyses."""
        summary_file = output_folder / "takeaways.md"
        
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write("# Analysis Summary\n\n")
            f.write(f"Generated: {self._get_timestamp()}\n\n")
            
            if results:
                f.write(f"**Provider**: {results[0].provider}\n")
                f.write(f"**Model**: {results[0].model}\n\n")
            
            f.write("## Key Insights\n\n")
            f.write("*This section would benefit from additional processing to extract key themes across all analyses.*\n\n")
            
            f.write("## Analysis Overview\n\n")
            for result in results:
                if not result.error:
                    f.write(f"- **{result.prompt_name}**: Completed\n")
                else:
                    f.write(f"- **{result.prompt_name}**: Error - {result.error}\n")
    
    def _save_multi_provider_summary(self, output_folder: Path, 
                                   multi_results: Dict[str, Any]) -> None:
        """Save comprehensive summary of multi-provider analysis."""
        summary_file = output_folder / "multi_provider_summary.md"
        
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write("# Multi-Provider Analysis Summary\n\n")
            f.write(f"Generated: {self._get_timestamp()}\n\n")
            
            # Basic info
            f.write("## Analysis Configuration\n\n")
            f.write(f"- **Analysis Type**: {multi_results.get('analysis_type', 'N/A')}\n")
            f.write(f"- **Providers Used**: {', '.join(multi_results.get('providers_used', []))}\n")
            f.write(f"- **Meta-Analysis Provider**: {multi_results.get('meta_provider', 'N/A')}\n\n")
            
            # Provider results summary
            f.write("## Provider Results Summary\n\n")
            provider_results = multi_results.get("provider_results", {})
            
            for provider, results in provider_results.items():
                f.write(f"### {provider.upper()}\n\n")
                
                if isinstance(results, dict) and "error" in results:
                    f.write(f"❌ **Error**: {results['error']}\n\n")
                elif isinstance(results, list):
                    success_count = len([r for r in results if not r.error])
                    error_count = len(results) - success_count
                    f.write(f"✅ **Successful analyses**: {success_count}\n")
                    f.write(f"❌ **Failed analyses**: {error_count}\n")
                    
                    if results:
                        f.write(f"**Model used**: {results[0].model}\n")
                    f.write("\n")
            
            # Meta-analysis summary
            meta_results = multi_results.get("meta_analysis", [])
            f.write("## Meta-Analysis Summary\n\n")
            
            if meta_results:
                success_count = len([r for r in meta_results if not r.error])
                error_count = len(meta_results) - success_count
                f.write(f"✅ **Successful meta-analyses**: {success_count}\n")
                f.write(f"❌ **Failed meta-analyses**: {error_count}\n\n")
                
                f.write("**Meta-analyses completed**:\n")
                for result in meta_results:
                    status = "✅" if not result.error else "❌"
                    prompt_name = result.prompt_name.replace("META_", "")
                    f.write(f"- {status} {prompt_name}\n")
            else:
                f.write("No meta-analysis performed.\n")
            
            f.write("\n## File Structure\n\n")
            f.write("```\n")
            f.write("multi_provider_review/\n")
            f.write("├── metadata.json\n")
            f.write("├── multi_provider_summary.md\n")
            
            for provider in provider_results.keys():
                if not (isinstance(provider_results[provider], dict) and "error" in provider_results[provider]):
                    f.write(f"├── {provider}/\n")
                    f.write(f"│   └── [analysis files]\n")
                else:
                    f.write(f"├── {provider}_error.txt\n")
            
            if meta_results:
                f.write("└── meta_analysis/\n")
                f.write("    └── [synthesized analyses]\n")
            
            f.write("```\n")
    
    def save_results_json(self, output_folder: Path, results: Any, 
                         filename: str = "results.json") -> None:
        """Save results as JSON for programmatic access."""
        json_file = output_folder / filename
        
        # Convert AnalysisResult objects to dictionaries
        if isinstance(results, dict):
            json_data = {}
            for key, value in results.items():
                if isinstance(value, list) and value and isinstance(value[0], AnalysisResult):
                    json_data[str(key)] = [asdict(result) for result in value]
                else:
                    json_data[str(key)] = value
        elif isinstance(results, list) and results and isinstance(results[0], AnalysisResult):
            json_data = [asdict(result) for result in results]
        else:
            json_data = results
        
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    def load_analysis_results(self, folder_path: str) -> Dict[str, Any]:
        """Load analysis results from a folder."""
        folder = Path(folder_path)
        
        if not folder.exists():
            raise FileNotFoundError(f"Analysis folder not found: {folder_path}")
        
        # Load metadata
        metadata_file = folder / "metadata.json"
        metadata = {}
        if metadata_file.exists():
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
        
        # Load results based on analysis type
        analysis_type = metadata.get("analysis_type", "unknown")
        
        if analysis_type == "chapter_review":
            return self._load_chapter_results(folder, metadata)
        elif analysis_type == "holistic_review":
            return self._load_holistic_results(folder, metadata)
        elif analysis_type == "transition_review":
            return self._load_transition_results(folder, metadata)
        else:
            return {"metadata": metadata, "files": list(folder.glob("*"))}
    
    def _load_chapter_results(self, folder: Path, metadata: Dict) -> Dict[str, Any]:
        """Load chapter analysis results."""
        chapter_files = list(folder.glob("chapter_*.md"))
        return {
            "metadata": metadata,
            "chapter_files": [str(f) for f in chapter_files],
            "chapter_count": len(chapter_files)
        }
    
    def _load_holistic_results(self, folder: Path, metadata: Dict) -> Dict[str, Any]:
        """Load holistic analysis results."""
        result_files = [f for f in folder.glob("*.txt") if f.name != "metadata.json"]
        return {
            "metadata": metadata,
            "result_files": [str(f) for f in result_files],
            "summary_file": str(folder / "takeaways.md") if (folder / "takeaways.md").exists() else None
        }
    
    def _load_transition_results(self, folder: Path, metadata: Dict) -> Dict[str, Any]:
        """Load transition analysis results."""
        transition_files = list(folder.glob("chapter_*_to_*.md"))
        return {
            "metadata": metadata,
            "transition_files": [str(f) for f in transition_files],
            "transition_count": len(transition_files)
        }
    
    def load_existing_multi_provider_analysis(self, analysis_folder: str) -> Dict[str, Any]:
        """Load existing multi-provider analysis results from folder."""
        folder_path = Path(analysis_folder)
        
        if not folder_path.exists():
            raise FileNotFoundError(f"Analysis folder not found: {analysis_folder}")
        
        # Load metadata
        metadata_file = folder_path / "metadata.json"
        if not metadata_file.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_file}")
        
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
        
        # Load provider results
        provider_results = {}
        
        # Check for individual provider folders
        for provider in ["openai", "anthropic", "gemini"]:
            provider_folder = folder_path / provider
            if provider_folder.exists():
                # Load all analysis files from this provider
                analysis_files = list(provider_folder.glob("*.txt"))
                provider_analyses = []
                
                for file_path in analysis_files:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # Parse the content to extract bad cop and good cop responses
                    parts = content.split("\n\nGOOD COP\n\n")
                    if len(parts) == 2:
                        bad_cop = parts[0].replace("BAD COP\n\n", "")
                        good_cop = parts[1]
                    else:
                        bad_cop = content
                        good_cop = ""
                    
                    # Create AnalysisResult-like object
                    from analysis_engine import AnalysisResult
                    result = AnalysisResult(
                        prompt_name=file_path.stem,
                        prompt_text="",  # We don't have the original prompt
                        bad_cop_response=bad_cop,
                        good_cop_response=good_cop,
                        provider=provider,
                        model=f"loaded_{provider}"
                    )
                    provider_analyses.append(result)
                
                provider_results[provider] = provider_analyses
            
            # Check for error files
            error_file = folder_path / f"{provider}_error.txt"  
            if error_file.exists():
                with open(error_file, "r") as f:
                    error_content = f.read()
                provider_results[provider] = {"error": error_content}
        
        return {
            "provider_results": provider_results,
            "metadata": metadata,
            "analysis_type": metadata.get("analysis_method", "holistic"),
            "providers_used": list(provider_results.keys()),
            "original_folder": str(folder_path)
        }
    
    def save_meta_analysis_to_existing_folder(self, folder_path: str, meta_results: List, 
                                            meta_provider: str) -> Path:
        """Save meta-analysis results to an existing analysis folder."""
        output_folder = Path(folder_path)
        
        if not output_folder.exists():
            raise FileNotFoundError(f"Output folder not found: {folder_path}")
        
        # Save meta-analysis results
        if meta_results:
            meta_folder = output_folder / "meta_analysis"
            meta_folder.mkdir(exist_ok=True)
            
            for result in meta_results:
                # Save meta-analysis with special formatting
                filename = result.prompt_name.replace("META_", "")
                with open(meta_folder / filename, "w", encoding="utf-8") as f:
                    f.write(f"# Meta-Analysis: {filename}\n\n")
                    f.write(f"**Original Prompt**: {result.prompt_text}\n\n")
                    f.write(f"**Meta-Provider**: {result.provider}\n")
                    f.write(f"**Meta-Model**: {result.model}\n\n")
                    f.write("## Synthesized Analysis\n\n")
                    f.write(result.bad_cop_response)
        
        # Update metadata to include meta-analysis info
        metadata_file = output_folder / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
            
            metadata["meta_provider"] = meta_provider
            metadata["meta_analysis_timestamp"] = self._get_timestamp()
            
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)
        
        # Update summary to include meta-analysis
        summary_file = output_folder / "multi_provider_summary.md"
        if summary_file.exists():
            with open(summary_file, "a", encoding="utf-8") as f:
                f.write(f"\n## Meta-Analysis Update\n\n")
                f.write(f"**Added**: {self._get_timestamp()}\n")
                f.write(f"**Meta-Provider**: {meta_provider}\n")
                
                success_count = len([r for r in meta_results if not r.error])
                error_count = len(meta_results) - success_count
                f.write(f"**Results**: {success_count} successful, {error_count} errors\n")
        
        return output_folder
    
    def list_recent_analyses(self, analysis_type: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent analysis folders."""
        if analysis_type:
            search_path = self.base_output_dir / analysis_type
        else:
            search_path = self.base_output_dir
        
        if not search_path.exists():
            return []
        
        # Find all analysis folders
        folders = []
        for folder in search_path.rglob("*"):
            if folder.is_dir() and (folder / "metadata.json").exists():
                try:
                    with open(folder / "metadata.json", "r") as f:
                        metadata = json.load(f)
                    folders.append({
                        "path": str(folder),
                        "timestamp": metadata.get("timestamp", ""),
                        "analysis_type": metadata.get("analysis_type", "unknown"),
                        "manuscript_path": metadata.get("manuscript_path", "")
                    })
                except:
                    continue
        
        # Sort by timestamp (newest first) and limit
        folders.sort(key=lambda x: x["timestamp"], reverse=True)
        return folders[:limit]