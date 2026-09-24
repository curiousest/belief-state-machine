#!/usr/bin/env python3
"""
CLI interface for literary manuscript analysis.
Provides command-line access to the analysis engine.
"""

import argparse
import sys
import os
import time
from pathlib import Path
from typing import List, Optional

# Auto-load .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file from current directory or parent directories
except ImportError:
    # dotenv not installed, skip auto-loading
    pass

from analysis_engine import ManuscriptAnalyzer, AnalysisConfig, MultiProviderAnalyzer
from prompts import prompt_library
from output_manager import OutputManager
from providers import ProviderFactory


def setup_api_keys(provider: str = None):
    """Ensure required API keys are available."""
    key_mappings = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY", 
        "gemini": "GOOGLE_API_KEY"
    }
    
    missing_keys = []
    
    if provider:
        # Check specific provider
        if provider in key_mappings:
            key_name = key_mappings[provider]
            if not os.getenv(key_name):
                missing_keys.append((provider, key_name))
    else:
        # Check all providers
        for prov, key_name in key_mappings.items():
            if not os.getenv(key_name):
                missing_keys.append((prov, key_name))
    
    if missing_keys:
        print("❌ Missing API keys:")
        for prov, key_name in missing_keys:
            print(f"   {prov}: {key_name}")
        
        print("\n📄 To fix this:")
        print("1. Create a .env file in this directory with:")
        for prov, key_name in missing_keys:
            print(f"   {key_name}=your-{prov}-key-here")
        
        print("\n2. Or set environment variables:")
        for prov, key_name in missing_keys:
            print(f"   export {key_name}='your-{prov}-key-here'")
        
        print(f"\n💡 The CLI will automatically load .env files")
        if provider:
            sys.exit(1)
        else:
            print("⚠️  Some providers may not work without their API keys")

def check_dotenv_available():
    """Check if python-dotenv is available and suggest installation."""
    try:
        import dotenv
        return True
    except ImportError:
        print("💡 Tip: Install python-dotenv for automatic .env file loading:")
        print("   pip install python-dotenv")
        print("   Then create a .env file with your API keys")
        return False


def print_manuscript_info(analyzer: ManuscriptAnalyzer, text: str):
    """Print basic manuscript information."""
    info = analyzer.get_manuscript_info(text)
    print(f"📄 Manuscript Info:")
    print(f"   Tokens: {info['token_count']:,}")
    print(f"   Chapters: {info['chapter_count']}")
    print(f"   Est. Pages: {info['estimated_pages']}")
    print()


def analyze_holistic(args):
    """Perform holistic manuscript analysis."""
    setup_api_keys(args.provider)
    
    # Use recommended model if none specified
    model = args.model
    if not model:
        recommended_models = ProviderFactory.get_recommended_models()
        model = recommended_models.get(args.provider)
        if not model:
            raise ValueError(f"No recommended model for provider: {args.provider}")
    
    config = AnalysisConfig(
        provider=args.provider,
        model=model,
        api_delay=args.delay,
        temperature=args.temperature
    )
    
    analyzer = ManuscriptAnalyzer(config)
    output_manager = OutputManager(args.output_dir)
    
    print(f"🔍 Loading manuscript: {args.manuscript}")
    text = analyzer.load_manuscript(args.manuscript)
    print_manuscript_info(analyzer, text)
    
    # Get prompts
    if args.prompts:
        prompts = prompt_library.get_custom_prompts(args.prompts)
        print(f"📝 Using custom prompts: {args.prompts}")
    else:
        prompts = prompt_library.holistic_analysis_prompts
        print(f"📝 Using all holistic analysis prompts ({len(prompts)} prompts)")
    
    print(f"🤖 Starting analysis with {config.provider}/{config.model}...")
    print(f"⏱️  Estimated time: {len(prompts) * config.api_delay / 60:.1f} minutes")
    print()
    
    # Perform analysis
    results = analyzer.analyze_full_manuscript(text, prompts)
    
    # Save results
    output_folder = output_manager.save_holistic_analysis(results, args.manuscript)
    output_manager.save_results_json(output_folder, results)
    
    print(f"✅ Analysis complete!")
    print(f"📁 Results saved to: {output_folder}")
    
    # Show summary
    error_count = sum(1 for r in results if r.error)
    success_count = len(results) - error_count
    print(f"📊 Summary: {success_count} successful, {error_count} errors")


def analyze_multi_provider(args):
    """Perform multi-provider analysis with meta-synthesis."""
    # Check all provider keys since we're using multiple
    setup_api_keys()
    
    if not check_dotenv_available():
        print()
    
    # Select providers to use
    providers = args.providers if args.providers else ["openai", "anthropic", "gemini"]
    available_providers = ProviderFactory.get_available_providers()
    
    # Validate providers
    invalid_providers = [p for p in providers if p not in available_providers]
    if invalid_providers:
        print(f"❌ Invalid providers: {invalid_providers}")
        print(f"Available providers: {list(available_providers.keys())}")
        sys.exit(1)
    
    base_config = AnalysisConfig(
        api_delay=args.delay,
        temperature=args.temperature
    )
    
    multi_analyzer = MultiProviderAnalyzer(providers, base_config)
    output_manager = OutputManager(args.output_dir)
    
    print(f"🔍 Loading manuscript: {args.manuscript}")
    # Use first provider's analyzer to load manuscript info
    first_analyzer = list(multi_analyzer.analyzers.values())[0]
    text = first_analyzer.load_manuscript(args.manuscript)
    print_manuscript_info(first_analyzer, text)
    
    # Get prompts
    if args.prompts:
        prompts = prompt_library.get_custom_prompts(args.prompts)
        print(f"📝 Using custom prompts: {args.prompts}")
    else:
        prompts = prompt_library.holistic_analysis_prompts
        print(f"📝 Using all holistic analysis prompts ({len(prompts)} prompts)")
    
    total_analyses = len(providers) * len(prompts) + len(prompts)  # +meta-analysis
    print(f"🤖 Starting multi-provider analysis...")
    print(f"📊 Providers: {', '.join(providers)}")
    print(f"🧠 Meta-analysis provider: {args.meta_provider}")
    print(f"⏱️  Estimated time: {total_analyses * base_config.api_delay / 60:.1f} minutes")
    print()
    
    # Perform multi-provider analysis
    results = multi_analyzer.run_complete_multi_provider_analysis(
        text=text,
        prompts=prompts,
        analysis_type="holistic",
        meta_provider=args.meta_provider
    )
    
    # Save results
    output_folder = output_manager.save_multi_provider_analysis(results, args.manuscript)
    output_manager.save_results_json(output_folder, results)
    
    print(f"✅ Multi-provider analysis complete!")
    print(f"📁 Results saved to: {output_folder}")
    
    # Show summary
    provider_results = results.get("provider_results", {})
    meta_results = results.get("meta_analysis", [])
    
    print(f"📊 Provider Summary:")
    for provider, prov_results in provider_results.items():
        if isinstance(prov_results, dict) and "error" in prov_results:
            print(f"   {provider}: ❌ Error")
        elif isinstance(prov_results, list):
            success_count = len([r for r in prov_results if not r.error])
            print(f"   {provider}: ✅ {success_count}/{len(prov_results)} successful")
    
    meta_success = len([r for r in meta_results if not r.error])
    print(f"🧠 Meta-analysis: ✅ {meta_success}/{len(meta_results)} successful")


def analyze_chapters(args):
    """Perform chapter-by-chapter analysis."""
    setup_api_keys(args.provider)
    
    # Use recommended model if none specified
    model = args.model
    if not model:
        recommended_models = ProviderFactory.get_recommended_models()
        model = recommended_models.get(args.provider)
        if not model:
            raise ValueError(f"No recommended model for provider: {args.provider}")
    
    config = AnalysisConfig(
        provider=args.provider,
        model=model,
        api_delay=args.delay,
        temperature=args.temperature
    )
    
    analyzer = ManuscriptAnalyzer(config)
    output_manager = OutputManager(args.output_dir)
    
    print(f"🔍 Loading manuscript: {args.manuscript}")
    text = analyzer.load_manuscript(args.manuscript)
    print_manuscript_info(analyzer, text)
    
    # Get prompts
    if args.prompts:
        prompts = prompt_library.get_custom_prompts(args.prompts)
        print(f"📝 Using custom prompts: {args.prompts}")
    else:
        prompts = prompt_library.chapter_analysis_prompts
        print(f"📝 Using all chapter analysis prompts ({len(prompts)} prompts)")
    
    info = analyzer.get_manuscript_info(text)
    total_analyses = info['chapter_count'] * len(prompts)
    
    print(f"🤖 Starting chapter analysis with {config.model}...")
    print(f"⏱️  Estimated time: {total_analyses * config.api_delay / 60:.1f} minutes")
    print()
    
    # Perform analysis
    results = analyzer.analyze_by_chapters(text, prompts)
    
    # Save results
    output_folder = output_manager.save_chapter_analysis(results, args.manuscript)
    output_manager.save_results_json(output_folder, results)
    
    print(f"✅ Analysis complete!")
    print(f"📁 Results saved to: {output_folder}")
    
    # Show summary
    total_results = sum(len(chapter_results) for chapter_results in results.values())
    error_count = sum(
        sum(1 for r in chapter_results if r.error) 
        for chapter_results in results.values()
    )
    success_count = total_results - error_count
    print(f"📊 Summary: {success_count} successful, {error_count} errors across {len(results)} chapters")


def analyze_single_chapter(args):
    """Perform analysis on a single chapter without splitting the file."""
    setup_api_keys(args.provider)
    
    # Use recommended model if none specified
    model = args.model
    if not model:
        recommended_models = ProviderFactory.get_recommended_models()
        model = recommended_models.get(args.provider)
        if not model:
            raise ValueError(f"No recommended model for provider: {args.provider}")
    
    config = AnalysisConfig(
        provider=args.provider,
        model=model,
        api_delay=args.delay,
        temperature=args.temperature
    )
    
    analyzer = ManuscriptAnalyzer(config)
    output_manager = OutputManager(args.output_dir)
    
    print(f"🔍 Loading manuscript: {args.manuscript}")
    text = analyzer.load_manuscript(args.manuscript)
    
    # Get manuscript info
    info = analyzer.get_manuscript_info(text)
    print(f"📄 Manuscript Info:")
    print(f"   Tokens: {info['token_count']:,}")
    print(f"   Chapters: {info['chapter_count']}")
    print(f"   Est. Pages: {info['estimated_pages']}")
    print()
    
    # Get prompts
    if args.prompts:
        prompts = prompt_library.get_custom_prompts(args.prompts)
        print(f"📝 Using custom prompts: {args.prompts}")
    else:
        prompts = prompt_library.chapter_analysis_prompts
        print(f"📝 Using all chapter analysis prompts ({len(prompts)} prompts)")
    
    total_analyses = len(prompts)
    
    print(f"🤖 Starting single chapter analysis with {config.model}...")
    print(f"⏱️  Estimated time: {total_analyses * config.api_delay / 60:.1f} minutes")
    print()
    
    # Perform analysis on the entire text as one unit
    results = []
    for prompt_name, prompt_text in prompts:
        print(f"  Analyzing: {prompt_name}")
        
        try:
            # Use the literary analyzer directly for single text analysis
            literary_analyzer = analyzer.analyzer
            result = literary_analyzer.analyze_text(text, prompt_text, prompt_name)
            results.append(result)
            
            # Add a small delay between API calls
            time.sleep(config.api_delay)
            
        except Exception as e:
            print(f"    ❌ Error analyzing {prompt_name}: {e}")
            # Create error result
            from analysis_engine import AnalysisResult
            error_result = AnalysisResult(
                prompt_name=prompt_name,
                prompt_text=prompt_text,
                bad_cop_response=f"Error: {str(e)}",
                good_cop_response=f"Error: {str(e)}",
                error=str(e),
                provider=config.provider,
                model=config.model
            )
            results.append(error_result)
    
    # Save results using holistic analysis format (since it's single text)
    output_folder = output_manager.save_holistic_analysis(results, args.manuscript)
    output_manager.save_results_json(output_folder, results)
    
    print(f"✅ Analysis complete!")
    print(f"📁 Results saved to: {output_folder}")
    
    # Show summary
    error_count = sum(1 for r in results if r.error)
    success_count = len(results) - error_count
    print(f"📊 Summary: {success_count} successful, {error_count} errors")


def analyze_transitions(args):
    """Perform transition analysis."""
    setup_api_keys(args.provider)
    
    # Use recommended model if none specified
    model = args.model
    if not model:
        recommended_models = ProviderFactory.get_recommended_models()
        model = recommended_models.get(args.provider)
        if not model:
            raise ValueError(f"No recommended model for provider: {args.provider}")
    
    config = AnalysisConfig(
        provider=args.provider,
        model=model,
        api_delay=args.delay,
        temperature=args.temperature
    )
    
    analyzer = ManuscriptAnalyzer(config)
    output_manager = OutputManager(args.output_dir)
    
    print(f"🔍 Loading manuscript: {args.manuscript}")
    text = analyzer.load_manuscript(args.manuscript)
    print_manuscript_info(analyzer, text)
    
    # Get prompts
    if args.prompts:
        prompts = prompt_library.get_custom_prompts(args.prompts)
        print(f"📝 Using custom prompts: {args.prompts}")
    else:
        prompts = prompt_library.transition_analysis_prompts
        print(f"📝 Using all transition analysis prompts ({len(prompts)} prompts)")
    
    info = analyzer.get_manuscript_info(text)
    transition_count = max(0, info['chapter_count'] - 1)
    total_analyses = transition_count * len(prompts)
    
    print(f"🤖 Starting transition analysis with {config.model}...")
    print(f"⏱️  Estimated time: {total_analyses * config.api_delay / 60:.1f} minutes")
    print()
    
    # Perform analysis
    results = analyzer.analyze_transitions(text, prompts)
    
    # Save results
    output_folder = output_manager.save_transition_analysis(results, args.manuscript)
    output_manager.save_results_json(output_folder, results)
    
    print(f"✅ Analysis complete!")
    print(f"📁 Results saved to: {output_folder}")
    
    # Show summary
    total_results = sum(len(transition_results) for transition_results in results.values())
    error_count = sum(
        sum(1 for r in transition_results if r.error) 
        for transition_results in results.values()
    )
    success_count = total_results - error_count
    print(f"📊 Summary: {success_count} successful, {error_count} errors across {len(results)} transitions")


def list_analyses(args):
    """List recent analyses."""
    output_manager = OutputManager(args.output_dir)
    analyses = output_manager.list_recent_analyses(args.type, args.limit)
    
    if not analyses:
        print("No analyses found.")
        return
    
    print(f"📋 Recent analyses ({len(analyses)}):")
    print()
    
    for analysis in analyses:
        manuscript_name = Path(analysis['manuscript_path']).name if analysis['manuscript_path'] else "Unknown"
        print(f"  {analysis['timestamp']} - {analysis['analysis_type']}")
        print(f"    📄 {manuscript_name}")
        print(f"    📁 {analysis['path']}")
        print()


def list_prompts(args):
    """List available prompts."""
    categories = prompt_library.all_categories
    
    if args.category:
        if args.category not in categories:
            print(f"Error: Unknown category '{args.category}'")
            print(f"Available categories: {list(categories.keys())}")
            return
        
        category = categories[args.category]
        print(f"📝 {category.name} Prompts:")
        print(f"   {category.description}")
        print()
        
        for name, prompt in category.prompts:
            print(f"  • {name}")
            if args.verbose:
                print(f"    {prompt[:100]}...")
            print()
    else:
        print("📚 Available Prompt Categories:")
        print()
        
        for key, category in categories.items():
            print(f"  {key}: {category.name}")
            print(f"    {category.description}")
            print(f"    {len(category.prompts)} prompts")
            print()
        
        print("Use --category <name> to see prompts in a specific category")


def list_providers(args):
    """List available providers and their models."""
    available_providers = ProviderFactory.get_available_providers()
    recommended_models = ProviderFactory.get_recommended_models()
    cost_efficient_models = ProviderFactory.get_cost_efficient_models()
    
    if args.verbose:
        model_capabilities = ProviderFactory.get_model_capabilities()
        provider_strengths = ProviderFactory.get_provider_strengths()
        
        print("🤖 Available AI Providers (Detailed)\n")
        
        for provider, models in available_providers.items():
            print(f"## {provider.upper()}")
            print(f"**Recommended for literary analysis**: {recommended_models.get(provider, 'N/A')}")
            print(f"**Cost-efficient option**: {cost_efficient_models.get(provider, 'N/A')}")
            
            print(f"\n**Strengths**:")
            strengths = provider_strengths.get(provider, [])
            for strength in strengths:
                print(f"  • {strength}")
            
            print(f"\n**Available models**: {len(models)} models")
            for model in models[:5]:  # Show first 5 models
                if model in model_capabilities:
                    cap = model_capabilities[model]
                    context = f"{cap['context_window']:,}" if cap['context_window'] else "Unknown"
                    strengths_text = ", ".join(cap.get('strengths', [])[:3])
                    print(f"  • {model} ({context} tokens) - {strengths_text}")
                else:
                    print(f"  • {model}")
            
            if len(models) > 5:
                print(f"  ... and {len(models) - 5} more models")
            
            print()
    else:
        print("🤖 Available AI Providers\n")
        
        for provider, models in available_providers.items():
            print(f"**{provider.upper()}**")
            print(f"  Recommended: {recommended_models.get(provider, 'N/A')}")
            print(f"  Cost-efficient: {cost_efficient_models.get(provider, 'N/A')}")
            print(f"  Total models: {len(models)}")
            print()
        
        print("💡 Use --verbose for detailed information")
        print("🔑 Set API keys in .env file:")
        print("   OPENAI_API_KEY=your-key")
        print("   ANTHROPIC_API_KEY=your-key") 
        print("   GOOGLE_API_KEY=your-key")


def analyze_meta_only(args):
    """Perform meta-analysis on existing multi-provider results."""
    setup_api_keys(args.meta_provider)
    
    output_manager = OutputManager(args.output_dir)
    
    print(f"🔍 Loading existing analysis from: {args.analysis_folder}")
    
    try:
        # Load existing results
        existing_results = output_manager.load_existing_multi_provider_analysis(args.analysis_folder)
        
        # Show what was loaded
        provider_results = existing_results.get("provider_results", {})
        print(f"📋 Found analyses from: {', '.join(provider_results.keys())}")
        
        successful_providers = []
        for provider, results in provider_results.items():
            if isinstance(results, list):
                successful_providers.append(provider)
                print(f"   ✅ {provider}: {len(results)} analyses")
            else:
                print(f"   ❌ {provider}: Error - {results.get('error', 'Unknown error')}")
        
        if not successful_providers:
            print("❌ No successful provider analyses found to synthesize")
            return
        
        # Get prompts from the loaded results (reconstruct from filenames)
        first_successful = provider_results[successful_providers[0]]
        prompts = [(result.prompt_name, result.prompt_text or f"Analysis prompt for {result.prompt_name}") 
                  for result in first_successful]
        
        print(f"🧠 Starting meta-analysis with {args.meta_provider}...")
        print(f"📝 Processing {len(prompts)} prompts")
        
        # Create meta-analyzer with specified provider
        base_config = AnalysisConfig(
            api_delay=args.delay,
            temperature=args.temperature
        )
        
        # We only need a meta-analyzer, not full multi-provider
        recommended_models = ProviderFactory.get_recommended_models()
        meta_config = AnalysisConfig(
            provider=args.meta_provider,
            model=args.model or recommended_models.get(args.meta_provider, ""),
            temperature=0.3,  # Lower temperature for synthesis
            api_delay=base_config.api_delay
        )
        
        from analysis_engine import LiteraryAnalyzer
        meta_analyzer = LiteraryAnalyzer(meta_config)
        
        # Generate meta-analysis
        meta_results = []
        
        for prompt_name, original_prompt in prompts:
            print(f"🔍 Synthesizing: {prompt_name}")
            
            # Collect all provider responses for this prompt
            provider_responses = []
            
            for provider, results in provider_results.items():
                if isinstance(results, dict) and "error" in results:
                    provider_responses.append(f"**{provider.upper()} ERROR**: {results['error']}")
                    continue
                
                # Find matching prompt result
                matching_result = next((r for r in results if r.prompt_name == prompt_name), None)
                
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
                
                from analysis_engine import AnalysisResult
                meta_result = AnalysisResult(
                    prompt_name=f"META_{prompt_name}",
                    prompt_text=original_prompt,
                    bad_cop_response=meta_response,
                    good_cop_response="",  # Meta-analysis doesn't use good/bad cop format
                    provider=f"meta_{args.meta_provider}",
                    model=f"synthesis_{meta_config.model}"
                )
                
                meta_results.append(meta_result)
                print(f"   ✅ Completed")
                
                # Rate limiting
                time.sleep(meta_config.api_delay)
                
            except Exception as e:
                from analysis_engine import AnalysisResult
                error_result = AnalysisResult(
                    prompt_name=f"META_{prompt_name}",
                    prompt_text=original_prompt,
                    bad_cop_response=f"Meta-analysis error: {str(e)}",
                    good_cop_response="",
                    error=str(e),
                    provider=f"meta_{args.meta_provider}",
                    model=f"synthesis_{meta_config.model}"
                )
                meta_results.append(error_result)
                print(f"   ❌ Error: {str(e)}")
        
        # Save meta-analysis back to original folder
        output_folder = output_manager.save_meta_analysis_to_existing_folder(
            args.analysis_folder, meta_results, args.meta_provider
        )
        
        print(f"\n✅ Meta-analysis complete!")
        print(f"📁 Results saved to: {output_folder}/meta_analysis/")
        
        # Show summary
        success_count = len([r for r in meta_results if not r.error])
        error_count = len(meta_results) - success_count
        print(f"📊 Summary: {success_count} successful, {error_count} errors")
        
    except Exception as e:
        print(f"❌ Error loading existing analysis: {str(e)}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Literary manuscript analysis tool with multi-provider support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s holistic manuscript.md --provider openai
  %(prog)s chapters manuscript.md --provider anthropic --prompts character_analysis.txt
  %(prog)s single-chapter manuscript.md --provider openai --prompts character_analysis.txt
  %(prog)s multi-provider manuscript.md --providers openai anthropic --meta-provider anthropic
  %(prog)s list-analyses --type multi_provider_review
  %(prog)s list-prompts --category chapter
  %(prog)s list-providers
        """
    )
    
    # Global options
    parser.add_argument('--output-dir', default='outputs', 
                       help='Output directory for results (default: outputs)')
    parser.add_argument('--provider', default='openai', 
                       choices=['openai', 'anthropic', 'gemini'],
                       help='AI provider to use (default: openai)')
    parser.add_argument('--model', 
                       help='Specific model to use (auto-selected if not provided)')
    parser.add_argument('--delay', type=float, default=2.0,
                       help='Delay between API calls in seconds (default: 2.0)')
    parser.add_argument('--temperature', type=float, default=0.7,
                       help='Model temperature (default: 0.7)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Holistic analysis
    holistic_parser = subparsers.add_parser('holistic', help='Perform holistic manuscript analysis')
    holistic_parser.add_argument('manuscript', help='Path to manuscript file')
    holistic_parser.add_argument('--prompts', nargs='+', 
                                help='Specific prompts to use (default: all holistic prompts)')
    holistic_parser.set_defaults(func=analyze_holistic)
    
    # Multi-provider analysis
    multi_parser = subparsers.add_parser('multi-provider', help='Perform multi-provider analysis with meta-synthesis')
    multi_parser.add_argument('manuscript', help='Path to manuscript file')
    multi_parser.add_argument('--providers', nargs='+', 
                             choices=['openai', 'anthropic', 'gemini'],
                             help='Providers to use (default: all three)')
    multi_parser.add_argument('--meta-provider', 
                             choices=['openai', 'anthropic', 'gemini'],
                             default='openai',
                             help='Provider for meta-analysis (default: openai)')
    multi_parser.add_argument('--prompts', nargs='+',
                             help='Specific prompts to use (default: all holistic prompts)')
    multi_parser.set_defaults(func=analyze_multi_provider)
    
    # Chapter analysis
    chapters_parser = subparsers.add_parser('chapters', help='Perform chapter-by-chapter analysis')
    chapters_parser.add_argument('manuscript', help='Path to manuscript file')
    chapters_parser.add_argument('--prompts', nargs='+',
                                help='Specific prompts to use (default: all chapter prompts)')
    chapters_parser.set_defaults(func=analyze_chapters)
    
    # Single chapter analysis
    single_chapter_parser = subparsers.add_parser('single-chapter', help='Perform analysis on a single chapter without splitting the file')
    single_chapter_parser.add_argument('manuscript', help='Path to manuscript file')
    single_chapter_parser.add_argument('--prompts', nargs='+',
                                       help='Specific prompts to use (default: all chapter prompts)')
    single_chapter_parser.set_defaults(func=analyze_single_chapter)
    
    # Transition analysis
    transitions_parser = subparsers.add_parser('transitions', help='Perform transition analysis')
    transitions_parser.add_argument('manuscript', help='Path to manuscript file')
    transitions_parser.add_argument('--prompts', nargs='+',
                                   help='Specific prompts to use (default: all transition prompts)')
    transitions_parser.set_defaults(func=analyze_transitions)
    
    # List analyses
    list_parser = subparsers.add_parser('list-analyses', help='List recent analyses')
    list_parser.add_argument('--type', choices=['holistic_review', 'chapter_review', 'transition_review', 'multi_provider_review'],
                            help='Filter by analysis type')
    list_parser.add_argument('--limit', type=int, default=10,
                            help='Maximum number of analyses to show (default: 10)')
    list_parser.set_defaults(func=list_analyses)
    
    # List prompts
    prompts_parser = subparsers.add_parser('list-prompts', help='List available prompts')
    prompts_parser.add_argument('--category', choices=['chapter', 'transition', 'holistic'],
                               help='Show prompts for specific category')
    prompts_parser.add_argument('--verbose', '-v', action='store_true',
                               help='Show prompt text preview')
    prompts_parser.set_defaults(func=list_prompts)
    
    # List providers
    providers_parser = subparsers.add_parser('list-providers', help='List available providers and models')
    providers_parser.add_argument('--verbose', '-v', action='store_true',
                                 help='Show detailed provider information')
    providers_parser.set_defaults(func=list_providers)
    
    # Meta-analysis only
    meta_parser = subparsers.add_parser('meta-analysis', help='Perform meta-analysis on existing results')
    meta_parser.add_argument('analysis_folder', help='Path to existing multi-provider analysis folder')
    meta_parser.add_argument('--meta-provider',
                           choices=['openai', 'anthropic', 'gemini'],
                           default='anthropic',
                           help='Provider for meta-analysis (default: anthropic)')
    meta_parser.set_defaults(func=analyze_meta_only)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n⚠️  Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()