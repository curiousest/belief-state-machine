"""
Core analysis engine for literary manuscript evaluation.
Abstracts the analysis logic from notebooks for reuse in CLI and other interfaces.
Supports multiple AI providers (OpenAI, Anthropic, Gemini).
"""

import os
import time
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import tiktoken
from providers import AIProvider, ProviderFactory


@dataclass
class AnalysisResult:
    """Container for analysis results."""
    prompt_name: str
    prompt_text: str
    bad_cop_response: str
    good_cop_response: str
    error: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None


@dataclass
class AnalysisConfig:
    """Configuration for analysis parameters."""
    provider: str = "openai"
    model: str = "o3"  # Best for literary analysis
    token_limit: int = 100000
    chunk_overlap: int = 300
    api_delay: float = 2.0
    temperature: float = 0.7
    max_tokens: int = 4000  # Default max tokens for responses
    api_key: Optional[str] = None


class TokenManager:
    """Handles tokenization and text chunking."""
    
    def __init__(self, provider: str = "openai", model: str = "o3"):
        # Use tiktoken for OpenAI models, fallback to approximation for others
        if provider == "openai" and model.startswith(("gpt", "o3", "o4")):
            try:
                self.encoding = tiktoken.encoding_for_model(model)
                self.use_tiktoken = True
            except:
                # Fallback if model not recognized by tiktoken
                self.encoding = tiktoken.get_encoding("cl100k_base")
                self.use_tiktoken = True
        else:
            # For Anthropic/Gemini, use approximation
            self.encoding = None
            self.use_tiktoken = False
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        if self.use_tiktoken and self.encoding:
            return len(self.encoding.encode(text))
        else:
            # Approximation: ~1.3 tokens per word for non-OpenAI models
            return int(len(text.split()) * 1.3)
    
    def split_into_chunks(self, text: str, max_tokens: int, overlap: int = 300) -> List[str]:
        """Split text into chunks based on headers, with fallback to character-based splitting."""
        # First try to split by headers
        raw_chunks = text.split("\n# ")
        
        chunks = []
        for i, chunk in enumerate(raw_chunks):
            if i == 0 and not text.startswith("# "):
                chunks.append(chunk)
            else:
                chunks.append("# " + chunk)
        
        merged_chunks = []
        current_chunk = ""
        
        for chunk in chunks:
            test_chunk = current_chunk + "\n\n" + chunk if current_chunk else chunk
            
            if self.count_tokens(test_chunk) > max_tokens:
                if current_chunk:
                    merged_chunks.append(current_chunk)
                current_chunk = chunk
            else:
                current_chunk = test_chunk
        
        if current_chunk:
            merged_chunks.append(current_chunk)
        
        # Check if any chunks are still too large and split them further
        final_chunks = []
        for chunk in merged_chunks:
            if self.count_tokens(chunk) <= max_tokens:
                final_chunks.append(chunk)
            else:
                # Split large chunks by sentences or paragraphs
                sub_chunks = self._split_large_chunk(chunk, max_tokens)
                final_chunks.extend(sub_chunks)
        
        return final_chunks
    
    def _split_large_chunk(self, chunk: str, max_tokens: int) -> List[str]:
        """Split a chunk that's too large into smaller pieces."""
        # Try splitting by paragraphs first
        paragraphs = chunk.split("\n\n")
        
        if len(paragraphs) > 1:
            sub_chunks = []
            current_sub_chunk = ""
            
            for paragraph in paragraphs:
                test_chunk = current_sub_chunk + "\n\n" + paragraph if current_sub_chunk else paragraph
                
                if self.count_tokens(test_chunk) > max_tokens:
                    if current_sub_chunk:
                        sub_chunks.append(current_sub_chunk)
                    current_sub_chunk = paragraph
                else:
                    current_sub_chunk = test_chunk
            
            if current_sub_chunk:
                sub_chunks.append(current_sub_chunk)
            
            # Check if any sub-chunks are still too large
            final_sub_chunks = []
            for sub_chunk in sub_chunks:
                if self.count_tokens(sub_chunk) <= max_tokens:
                    final_sub_chunks.append(sub_chunk)
                else:
                    # Split by sentences as last resort
                    sentences = sub_chunk.split(". ")
                    sentence_chunks = []
                    current_sentence_chunk = ""
                    
                    for sentence in sentences:
                        test_chunk = current_sentence_chunk + ". " + sentence if current_sentence_chunk else sentence
                        
                        if self.count_tokens(test_chunk) > max_tokens:
                            if current_sentence_chunk:
                                sentence_chunks.append(current_sentence_chunk)
                            current_sentence_chunk = sentence
                        else:
                            current_sentence_chunk = test_chunk
                    
                    if current_sentence_chunk:
                        sentence_chunks.append(current_sentence_chunk)
                    
                    final_sub_chunks.extend(sentence_chunks)
            
            return final_sub_chunks
        else:
            # If no paragraphs, split by sentences
            sentences = chunk.split(". ")
            sentence_chunks = []
            current_sentence_chunk = ""
            
            for sentence in sentences:
                test_chunk = current_sentence_chunk + ". " + sentence if current_sentence_chunk else sentence
                
                if self.count_tokens(test_chunk) > max_tokens:
                    if current_sentence_chunk:
                        sentence_chunks.append(current_sentence_chunk)
                    current_sentence_chunk = sentence
                else:
                    current_sentence_chunk = test_chunk
            
            if current_sentence_chunk:
                sentence_chunks.append(current_sentence_chunk)
            
            return sentence_chunks
    
    def split_into_chapters(self, text: str) -> List[str]:
        """Split text into chapters."""
        chapters = text.split("\n## Chapter ")
        
        processed_chapters = []
        for i, chapter in enumerate(chapters):
            if i == 0:
                if chapter.strip():
                    processed_chapters.append(chapter)
            else:
                processed_chapters.append("## Chapter " + chapter)
        
        return processed_chapters


class LiteraryAnalyzer:
    """Core analyzer that performs literary analysis using AI."""
    
    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.token_manager = TokenManager(config.provider, config.model)
        self.provider = ProviderFactory.create_provider(
            provider_type=config.provider,
            model=config.model,
            api_key=config.api_key,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            api_delay=config.api_delay
        )
    
    def analyze_text(self, text: str, prompt: str, prompt_name: str = "") -> AnalysisResult:
        """Analyze text with given prompt using bad cop/good cop approach."""
        try:
            # Bad cop analysis
            bad_cop_response = self._get_analysis(
                text, prompt, 
                "You are a bad cop literary structural analyst."
            )
            
            # Good cop analysis (building on bad cop)
            good_cop_response = self._get_analysis(
                text, prompt,
                "You are the 'good cop' literary structural analyst.",
                previous_analysis=bad_cop_response
            )
            
            return AnalysisResult(
                prompt_name=prompt_name,
                prompt_text=prompt,
                bad_cop_response=bad_cop_response,
                good_cop_response=good_cop_response,
                provider=self.config.provider,
                model=self.config.model
            )
            
        except Exception as e:
            error_msg = f"Error in analysis: {str(e)}"
            return AnalysisResult(
                prompt_name=prompt_name,
                prompt_text=prompt,
                bad_cop_response=error_msg,
                good_cop_response=error_msg,
                error=error_msg,
                provider=self.config.provider,
                model=self.config.model
            )
    
    def _combine_chunk_results(self, chunk_results: List[AnalysisResult], prompt_name: str, prompt_text: str) -> AnalysisResult:
        """Combine results from multiple chunks into a single analysis result."""
        # Extract bad cop and good cop responses from all chunks
        bad_cop_responses = []
        good_cop_responses = []
        errors = []
        
        for chunk_result in chunk_results:
            if chunk_result.error:
                errors.append(f"Chunk {chunk_result.prompt_name}: {chunk_result.error}")
            else:
                bad_cop_responses.append(chunk_result.bad_cop_response)
                good_cop_responses.append(chunk_result.good_cop_response)
        
        # If there were errors, return error result
        if errors:
            error_msg = f"Errors in chunk analysis: {'; '.join(errors)}"
            return AnalysisResult(
                prompt_name=prompt_name,
                prompt_text=prompt_text,
                bad_cop_response=error_msg,
                good_cop_response=error_msg,
                error=error_msg,
                provider=self.config.provider,
                model=self.config.model
            )
        
        # Combine the responses
        combined_bad_cop = "\n\n---\n\n".join(bad_cop_responses)
        combined_good_cop = "\n\n---\n\n".join(good_cop_responses)
        
        return AnalysisResult(
            prompt_name=prompt_name,
            prompt_text=prompt_text,
            bad_cop_response=combined_bad_cop,
            good_cop_response=combined_good_cop,
            provider=self.config.provider,
            model=self.config.model
        )
    
    def _get_analysis(self, text: str, prompt: str, system_prompt: str, 
                     previous_analysis: str = None) -> str:
        """Get analysis from AI provider."""
        messages = [
            self.provider.format_system_message(system_prompt)
        ]
        
        if previous_analysis:
            # Good cop follows bad cop
            messages.extend([
                self.provider.format_user_message(f"{prompt} Provide excessive critical feedback for improvement. Here is the manuscript:\n\n{text}"),
                self.provider.format_assistant_message(previous_analysis),
                self.provider.format_user_message("Now you are the 'good cop' literary structural analyst. Provide excessive praise critical feedback.")
            ])
        else:
            # Bad cop initial analysis
            full_prompt = f"{prompt} Provide excessive critical feedback for improvement with neutral tone. BE SPECIFIC about exact locations of the piece when giving feedback. Here is the manuscript:\n\n{text}"
            messages.append(self.provider.format_user_message(full_prompt))
        
        return self.provider.generate_response(messages)
    
    def analyze_with_prompts(self, text: str, prompts: List[Tuple[str, str]]) -> List[AnalysisResult]:
        """Analyze text with multiple prompts."""
        results = []
        
        # Check if text needs chunking (limit to 25,000 tokens to stay well under rate limit)
        token_count = self.token_manager.count_tokens(text)
        max_tokens_per_chunk = 25000  # Conservative limit to stay well under 40k rate limit
        
        if token_count > max_tokens_per_chunk:
            print(f"📄 Text is {token_count:,} tokens, chunking into smaller pieces...")
            chunks = self.token_manager.split_into_chunks(text, max_tokens_per_chunk, self.config.chunk_overlap)
            print(f"📄 Split into {len(chunks)} chunks")
            
            for prompt_name, prompt_text in prompts:
                print(f"Analyzing: {prompt_name}")
                
                # Analyze each chunk and combine results
                chunk_results = []
                for i, chunk in enumerate(chunks):
                    print(f"  Processing chunk {i+1}/{len(chunks)} ({self.token_manager.count_tokens(chunk):,} tokens)")
                    chunk_result = self.analyze_text(chunk, prompt_text, f"{prompt_name}_chunk_{i+1}")
                    chunk_results.append(chunk_result)
                    time.sleep(self.config.api_delay)
                
                # Combine chunk results into a single result
                combined_result = self._combine_chunk_results(chunk_results, prompt_name, prompt_text)
                results.append(combined_result)
                
                # Rate limiting delay between prompts
                time.sleep(self.config.api_delay)
        else:
            # Original behavior for smaller texts
            for prompt_name, prompt_text in prompts:
                print(f"Analyzing: {prompt_name}")
                
                result = self.analyze_text(text, prompt_text, prompt_name)
                results.append(result)
                
                # Rate limiting delay
                time.sleep(self.config.api_delay)
        
        return results
    
    def analyze_chapters(self, text: str, prompts: List[Tuple[str, str]]) -> Dict[int, List[AnalysisResult]]:
        """Analyze text split into chapters."""
        chapters = self.token_manager.split_into_chapters(text)
        chapter_results = {}
        
        for chapter_idx, chapter_text in enumerate(chapters):
            if not chapter_text.strip():
                continue
                
            print(f"Processing Chapter {chapter_idx}...")
            chapter_results[chapter_idx] = self.analyze_with_prompts(chapter_text, prompts)
        
        return chapter_results
    
    def analyze_transitions(self, text: str, prompts: List[Tuple[str, str]]) -> Dict[str, List[AnalysisResult]]:
        """Analyze transitions between chapters."""
        chapters = self.token_manager.split_into_chapters(text)
        transition_results = {}
        
        for chapter_idx in range(len(chapters) - 1):
            if not chapters[chapter_idx].strip() or not chapters[chapter_idx + 1].strip():
                continue
            
            transition_key = f"chapter_{chapter_idx}_to_{chapter_idx + 1}"
            transition_text = chapters[chapter_idx] + "\n\n" + chapters[chapter_idx + 1]
            
            print(f"Analyzing transition: {transition_key}")
            transition_results[transition_key] = self.analyze_with_prompts(transition_text, prompts)
        
        return transition_results


class ManuscriptAnalyzer:
    """High-level interface for manuscript analysis."""
    
    def __init__(self, config: AnalysisConfig = None):
        self.config = config or AnalysisConfig()
        self.analyzer = LiteraryAnalyzer(self.config)
        self.token_manager = TokenManager(self.config.provider, self.config.model)
    
    def load_manuscript(self, file_path: str) -> str:
        """Load manuscript from file."""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    
    def get_manuscript_info(self, text: str) -> Dict[str, Any]:
        """Get basic info about manuscript."""
        token_count = self.token_manager.count_tokens(text)
        chapters = self.token_manager.split_into_chapters(text)
        
        return {
            "token_count": token_count,
            "chapter_count": len([ch for ch in chapters if ch.strip()]),
            "estimated_pages": token_count // 250,  # Rough estimate
        }
    
    def analyze_full_manuscript(self, text: str, prompts: List[Tuple[str, str]]) -> List[AnalysisResult]:
        """Analyze entire manuscript as single unit."""
        return self.analyzer.analyze_with_prompts(text, prompts)
    
    def analyze_by_chapters(self, text: str, prompts: List[Tuple[str, str]]) -> Dict[int, List[AnalysisResult]]:
        """Analyze manuscript chapter by chapter."""
        return self.analyzer.analyze_chapters(text, prompts)
    
    def analyze_transitions(self, text: str, prompts: List[Tuple[str, str]]) -> Dict[str, List[AnalysisResult]]:
        """Analyze transitions between chapters."""
        return self.analyzer.analyze_transitions(text, prompts)


class MultiProviderAnalyzer:
    """Analyzer that can run analysis across multiple AI providers and perform meta-analysis."""
    
    def __init__(self, providers: List[str] = None, base_config: AnalysisConfig = None):
        """Initialize with list of providers to use."""
        self.providers = providers or ["openai", "anthropic", "gemini"]
        self.base_config = base_config or AnalysisConfig()
        self.analyzers = {}
        self.recommended_models = ProviderFactory.get_recommended_models()
        
        # Create analyzer for each provider
        for provider in self.providers:
            config = AnalysisConfig(
                provider=provider,
                model=self.recommended_models.get(provider, ""),
                token_limit=self.base_config.token_limit,
                chunk_overlap=self.base_config.chunk_overlap,
                api_delay=self.base_config.api_delay,
                temperature=self.base_config.temperature
            )
            self.analyzers[provider] = ManuscriptAnalyzer(config)
    
    def analyze_with_all_providers(self, text: str, prompts: List[Tuple[str, str]], 
                                 analysis_type: str = "holistic") -> Dict[str, Any]:
        """Run analysis with all configured providers."""
        results = {}
        
        for provider in self.providers:
            print(f"\n🤖 Running analysis with {provider} ({self.recommended_models[provider]})...")
            
            try:
                analyzer = self.analyzers[provider]
                
                if analysis_type == "holistic":
                    provider_results = analyzer.analyze_full_manuscript(text, prompts)
                elif analysis_type == "chapters":
                    provider_results = analyzer.analyze_by_chapters(text, prompts)
                elif analysis_type == "transitions":
                    provider_results = analyzer.analyze_transitions(text, prompts)
                else:
                    raise ValueError(f"Unknown analysis type: {analysis_type}")
                
                results[provider] = provider_results
                print(f"✅ {provider} analysis complete")
                
            except Exception as e:
                print(f"❌ Error with {provider}: {str(e)}")
                results[provider] = {"error": str(e)}
        
        return results
    
    def generate_meta_analysis(self, multi_provider_results: Dict[str, Any], 
                             prompts: List[Tuple[str, str]], 
                             meta_provider: str = "anthropic") -> List[AnalysisResult]:
        """Generate meta-analysis combining insights from all providers."""
        print(f"\n🔍 Generating meta-analysis with {meta_provider}...")
        
        # Use specified provider for meta-analysis
        meta_config = AnalysisConfig(
            provider=meta_provider,
            model=self.recommended_models.get(meta_provider, ""),
            temperature=0.3,  # Lower temperature for synthesis
            api_delay=self.base_config.api_delay
        )
        meta_analyzer = LiteraryAnalyzer(meta_config)
        
        meta_results = []
        
        for prompt_name, original_prompt in prompts:
            # Collect all provider responses for this prompt
            provider_responses = []
            
            for provider, results in multi_provider_results.items():
                if isinstance(results, dict) and "error" in results:
                    provider_responses.append(f"**{provider.upper()} ERROR**: {results['error']}")
                    continue
                
                # Find matching prompt result
                if isinstance(results, list):  # Holistic analysis
                    matching_result = next((r for r in results if r.prompt_name == prompt_name), None)
                elif isinstance(results, dict):  # Chapter/transition analysis
                    # For now, just take first chapter/transition for meta-analysis
                    first_key = next(iter(results.keys()), None)
                    if first_key:
                        chapter_results = results[first_key]
                        matching_result = next((r for r in chapter_results if r.prompt_name == prompt_name), None)
                    else:
                        matching_result = None
                else:
                    matching_result = None
                
                if matching_result and not matching_result.error:
                    response_text = f"""
**{provider.upper()} ({matching_result.model}) ANALYSIS**:

*Bad Cop Response:*
{matching_result.bad_cop_response}

*Good Cop Response:*
{matching_result.good_cop_response}
"""
                    provider_responses.append(response_text)
                else:
                    provider_responses.append(f"**{provider.upper()}**: No valid response for {prompt_name}")
            
            # Create meta-analysis prompt
            combined_responses = "\n\n" + "="*50 + "\n\n".join(provider_responses)
            
            meta_prompt = f"""
You are conducting a meta-analysis of literary criticism. You have received analyses of the same manuscript from multiple AI systems with different strengths:

- OpenAI (o3): Excels at reasoning and logical analysis
- Anthropic (Claude): Strong at nuanced literary understanding and cultural sensitivity  
- Google (Gemini): Good at pattern recognition and thinking through complex texts

Your task is to synthesize these multiple perspectives into a comprehensive meta-analysis that:
1. Identifies points of convergence and divergence between the analyses
2. Highlights the most insightful observations from each provider
3. Resolves contradictions by weighing the evidence
4. Provides a synthesized recommendation that incorporates the best insights from all sources

ORIGINAL PROMPT: {original_prompt}

MULTIPLE PROVIDER ANALYSES:
{combined_responses}

Please provide a comprehensive meta-analysis that synthesizes these perspectives:
"""
            
            # Generate meta-analysis
            try:
                meta_response = meta_analyzer._get_analysis(
                    text="",  # Text already included in prompt
                    prompt=meta_prompt,
                    system_prompt="You are an expert meta-analyst synthesizing literary criticism from multiple AI perspectives. Provide thoughtful, balanced synthesis that identifies the strongest insights from each source."
                )
                
                meta_result = AnalysisResult(
                    prompt_name=f"META_{prompt_name}",
                    prompt_text=original_prompt,
                    bad_cop_response=meta_response,
                    good_cop_response="",  # Meta-analysis doesn't use good/bad cop format
                    provider=f"meta_{meta_provider}",
                    model=f"synthesis_{self.recommended_models.get(meta_provider, '')}"
                )
                
                meta_results.append(meta_result)
                print(f"✅ Meta-analysis complete for {prompt_name}")
                
                # Rate limiting
                time.sleep(meta_config.api_delay)
                
            except Exception as e:
                error_result = AnalysisResult(
                    prompt_name=f"META_{prompt_name}",
                    prompt_text=original_prompt,
                    bad_cop_response=f"Meta-analysis error: {str(e)}",
                    good_cop_response="",
                    error=str(e),
                    provider=f"meta_{meta_provider}",
                    model=f"synthesis_{self.recommended_models.get(meta_provider, '')}"
                )
                meta_results.append(error_result)
                print(f"❌ Meta-analysis error for {prompt_name}: {str(e)}")
        
        return meta_results
    
    def run_complete_multi_provider_analysis(self, text: str, prompts: List[Tuple[str, str]], 
                                           analysis_type: str = "holistic", 
                                           meta_provider: str = "anthropic") -> Dict[str, Any]:
        """Run complete analysis with all providers plus meta-analysis."""
        print(f"🚀 Starting multi-provider {analysis_type} analysis...")
        print(f"📋 Providers: {', '.join(self.providers)}")
        print(f"🧠 Meta-analysis provider: {meta_provider}")
        print(f"📝 Prompts: {len(prompts)}")
        
        # Run analysis with all providers
        multi_results = self.analyze_with_all_providers(text, prompts, analysis_type)
        
        # Generate meta-analysis
        meta_results = self.generate_meta_analysis(multi_results, prompts, meta_provider)
        
        return {
            "provider_results": multi_results,
            "meta_analysis": meta_results,
            "analysis_type": analysis_type,
            "providers_used": self.providers,
            "meta_provider": meta_provider
        }