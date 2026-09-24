"""
AI provider abstraction layer for literary analysis.
Supports OpenAI, Anthropic, and Google Gemini providers with latest 2025 models.
Optimized for long-form text analysis and literary criticism.
"""

import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import time


@dataclass
class ProviderConfig:
    """Configuration for AI providers."""
    provider_type: str
    model: str
    api_key: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    api_delay: float = 2.0


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
    
    @abstractmethod
    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate response from the AI model."""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model."""
        pass
    
    def format_system_message(self, content: str) -> Dict[str, str]:
        """Format system message for the provider."""
        return {"role": "system", "content": content}
    
    def format_user_message(self, content: str) -> Dict[str, str]:
        """Format user message for the provider."""
        return {"role": "user", "content": content}
    
    def format_assistant_message(self, content: str) -> Dict[str, str]:
        """Format assistant message for the provider."""
        return {"role": "assistant", "content": content}


class OpenAIProvider(AIProvider):
    """OpenAI provider implementation with latest 2025 models."""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        try:
            import openai
            self.client = openai.OpenAI(api_key=config.api_key)
        except ImportError:
            raise ImportError("OpenAI library not installed. Run: pip install openai")
    
    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate response using OpenAI API."""
        # Different models use different parameter names for max tokens
        kwargs = {
            "model": self.config.model,
            "messages": messages,
        }
        
        # o3 models have restrictions on parameters
        if self.config.model.startswith("o3") or self.config.model.startswith("o4"):
            # o3 models only support default temperature (1) and use max_completion_tokens
            if self.config.max_tokens:
                kwargs["max_completion_tokens"] = self.config.max_tokens
        else:
            # Other models support custom temperature and max_tokens
            kwargs["temperature"] = self.config.temperature
            if self.config.max_tokens:
                kwargs["max_tokens"] = self.config.max_tokens
        
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get OpenAI model information."""
        return {
            "provider": "openai",
            "model": self.config.model,
            "supports_system_messages": True,
            "context_window": self._get_context_window()
        }
    
    def _get_context_window(self) -> int:
        """Get context window size for the model."""
        model_contexts = {
            # Latest 2025 models
            "gpt-4.1": 1000000,  # 1M tokens
            "gpt-4.1-mini": 1000000,
            "gpt-4.1-nano": 1000000,
            "o3": 128000,  # Reasoning model
            "o4-mini": 128000,  # Fast reasoning model
            "gpt-4o": 128000,  # Standard multimodal
            "gpt-4.5": 128000,  # Being phased out
            # Legacy models
            "gpt-4-0125-preview": 128000,
            "gpt-4-turbo-preview": 128000,
            "gpt-4": 8192,
            "gpt-4-32k": 32768,
            "gpt-3.5-turbo": 4096,
            "gpt-3.5-turbo-16k": 16384
        }
        return model_contexts.get(self.config.model, 128000)


class AnthropicProvider(AIProvider):
    """Anthropic provider implementation with latest 2025 Claude models."""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=config.api_key)
        except ImportError:
            raise ImportError("Anthropic library not installed. Run: pip install anthropic")
    
    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate response using Anthropic API."""
        # Anthropic uses a different message format
        system_message = None
        conversation = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                conversation.append(msg)
        
        kwargs = {
            "model": self.config.model,
            "messages": conversation,
            "temperature": self.config.temperature,
        }
        
        if system_message:
            kwargs["system"] = system_message
            
        if self.config.max_tokens:
            kwargs["max_tokens"] = self.config.max_tokens
        else:
            kwargs["max_tokens"] = 4096  # Anthropic requires max_tokens
        
        response = self.client.messages.create(**kwargs)
        return response.content[0].text
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Anthropic model information."""
        return {
            "provider": "anthropic",
            "model": self.config.model,
            "supports_system_messages": True,
            "context_window": self._get_context_window()
        }
    
    def _get_context_window(self) -> int:
        """Get context window size for the model."""
        model_contexts = {
            # Latest 2025 Claude 4 models
            "claude-opus-4": 200000,
            "claude-sonnet-4": 200000,
            # Claude 3.7 with extended thinking
            "claude-3.7-sonnet": 200000,
            # Claude 3.5 series
            "claude-3-5-sonnet-20241022": 200000,
            "claude-3-5-sonnet-20240620": 200000,
            "claude-3-5-haiku": 200000,
            # Claude 3 series
            "claude-3-opus-20240229": 200000,
            "claude-3-sonnet-20240229": 200000,
            "claude-3-haiku-20240307": 200000,
            # Legacy models (retired)
            "claude-2.1": 200000,
            "claude-2.0": 100000,
            "claude-instant-1.2": 100000
        }
        return model_contexts.get(self.config.model, 200000)


class GeminiProvider(AIProvider):
    """Google Gemini provider implementation with latest 2025 models."""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        try:
            import google.generativeai as genai
            genai.configure(api_key=config.api_key)
            self.client = genai.GenerativeModel(config.model)
        except ImportError:
            raise ImportError("Google AI library not installed. Run: pip install google-generativeai")
    
    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate response using Gemini API."""
        # Convert messages to Gemini format
        conversation = []
        system_instruction = None
        
        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            elif msg["role"] == "user":
                conversation.append({"role": "user", "parts": [msg["content"]]})
            elif msg["role"] == "assistant":
                conversation.append({"role": "model", "parts": [msg["content"]]})
        
        generation_config = {
            "temperature": self.config.temperature,
        }
        
        if self.config.max_tokens:
            generation_config["max_output_tokens"] = self.config.max_tokens
        
        # Create new model instance with system instruction if needed
        if system_instruction:
            import google.generativeai as genai
            model = genai.GenerativeModel(
                self.config.model,
                system_instruction=system_instruction
            )
        else:
            model = self.client
        
        # Start chat if multiple messages, otherwise use generate_content
        if len(conversation) > 1:
            chat = model.start_chat(history=conversation[:-1])
            response = chat.send_message(
                conversation[-1]["parts"][0],
                generation_config=generation_config
            )
        else:
            response = model.generate_content(
                conversation[0]["parts"][0] if conversation else "",
                generation_config=generation_config
            )
        
        return response.text
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Gemini model information."""
        return {
            "provider": "gemini",
            "model": self.config.model,
            "supports_system_messages": True,
            "context_window": self._get_context_window()
        }
    
    def _get_context_window(self) -> int:
        """Get context window size for the model."""
        model_contexts = {
            # Latest 2025 Gemini 2.5 series
            "gemini-2.5-pro": 1000000,  # 1M tokens, 2M coming soon
            "gemini-2.5-flash": 1000000,  # 1M tokens
            # Gemini 2.0 series
            "gemini-2.0-flash": 1000000,  # 1M tokens
            "gemini-2.0-flash-lite": 1000000,
            "gemini-2.0-pro-experimental": 1000000,
            # Legacy Gemini 1.5 series
            "gemini-1.5-pro": 1048576,  # 1M tokens
            "gemini-1.5-flash": 1048576,  # 1M tokens
            # Legacy Gemini 1.0 series
            "gemini-pro": 30720,
            "gemini-pro-vision": 12288
        }
        return model_contexts.get(self.config.model, 1000000)


class ProviderFactory:
    """Factory for creating AI providers."""
    
    @staticmethod
    def create_provider(provider_type: str, model: str, api_key: str = None, **kwargs) -> AIProvider:
        """Create an AI provider instance."""
        
        # Get API key from environment if not provided
        if not api_key:
            if provider_type == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
            elif provider_type == "anthropic":
                api_key = os.getenv("ANTHROPIC_API_KEY")
            elif provider_type == "gemini":
                api_key = os.getenv("GOOGLE_API_KEY")
            
            if not api_key:
                raise ValueError(f"API key not provided for {provider_type}. Set environment variable or pass api_key parameter.")
        
        config = ProviderConfig(
            provider_type=provider_type,
            model=model,
            api_key=api_key,
            **kwargs
        )
        
        if provider_type == "openai":
            return OpenAIProvider(config)
        elif provider_type == "anthropic":
            return AnthropicProvider(config)
        elif provider_type == "gemini":
            return GeminiProvider(config)
        else:
            raise ValueError(f"Unsupported provider: {provider_type}")
    
    @staticmethod
    def get_available_providers() -> Dict[str, List[str]]:
        """Get available providers and their models (2025 latest)."""
        return {
            "openai": [
                # Latest 2025 models
                "o3",  # Best for reasoning and analysis
                "o4-mini",  # Fast reasoning
                "gpt-4.1",  # Latest with 1M context
                "gpt-4.1-mini", 
                "gpt-4.1-nano",
                "gpt-4o",  # Standard multimodal
                # Legacy models
                "gpt-4-0125-preview",
                "gpt-4-turbo-preview",
                "gpt-4",
                "gpt-3.5-turbo"
            ],
            "anthropic": [
                # Latest 2025 Claude 4 models
                "claude-opus-4",
                "claude-sonnet-4",
                # Claude 3.7 with extended thinking
                "claude-3.7-sonnet",
                # Claude 3.5 series
                "claude-3-5-sonnet-20241022",
                "claude-3-5-sonnet-20240620",
                "claude-3-5-haiku",
                # Claude 3 series
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ],
            "gemini": [
                # Latest 2025 Gemini 2.5 series
                "gemini-2.5-pro",
                "gemini-2.5-flash",
                # Gemini 2.0 series
                "gemini-2.0-flash",
                "gemini-2.0-flash-lite",
                "gemini-2.0-pro-experimental",
                # Legacy models
                "gemini-1.5-pro",
                "gemini-1.5-flash",
                "gemini-pro"
            ]
        }
    
    @staticmethod
    def get_recommended_models() -> Dict[str, str]:
        """Get recommended models for literary analysis (2025 latest)."""
        return {
            "openai": "o3",  # Best reasoning for complex literary analysis, affordable after 80% price cut
            "anthropic": "claude-3.7-sonnet",  # Extended thinking capabilities for deep analysis
            "gemini": "gemini-2.5-pro"  # Advanced model with built-in thinking for textual analysis
        }
    
    @staticmethod
    def get_cost_efficient_models() -> Dict[str, str]:
        """Get cost-efficient models for each provider."""
        return {
            "openai": "o4-mini",  # Fast, cost-efficient reasoning
            "anthropic": "claude-sonnet-4",  # Balanced performance/cost
            "gemini": "gemini-2.5-flash"  # Cost-efficient with reasoning
        }
    
    @staticmethod
    def get_model_capabilities() -> Dict[str, Dict[str, Any]]:
        """Get detailed capabilities for literary analysis models."""
        return {
            "o3": {
                "provider": "openai",
                "context_window": 128000,
                "strengths": ["complex_reasoning", "literary_interpretation", "analytical_depth", "philosophical_analysis"],
                "pricing_tier": "mid",  # After 80% price cut
                "best_for": "Deep literary analysis requiring complex reasoning"
            },
            "o4-mini": {
                "provider": "openai",
                "context_window": 128000,
                "strengths": ["fast_reasoning", "cost_efficient", "good_analysis"],
                "pricing_tier": "low",
                "best_for": "Quick literary analysis on a budget"
            },
            "claude-3.7-sonnet": {
                "provider": "anthropic",
                "context_window": 200000,
                "strengths": ["extended_thinking", "nuanced_analysis", "cultural_sensitivity", "literary_sophistication"],
                "pricing_tier": "mid",
                "best_for": "Sophisticated literary criticism with extended reasoning"
            },
            "claude-sonnet-4": {
                "provider": "anthropic",
                "context_window": 200000,
                "strengths": ["balanced_performance", "good_analysis", "reliable_output"],
                "pricing_tier": "mid",
                "best_for": "Reliable literary analysis with good cost-performance balance"
            },
            "gemini-2.5-pro": {
                "provider": "gemini",
                "context_window": 1000000,
                "strengths": ["built_in_thinking", "long_context", "textual_analysis", "pattern_recognition"],
                "pricing_tier": "mid",
                "best_for": "Large manuscript analysis with built-in reasoning"
            },
            "gemini-2.5-flash": {
                "provider": "gemini",
                "context_window": 1000000,
                "strengths": ["cost_efficient", "long_context", "fast_processing"],
                "pricing_tier": "low",
                "best_for": "Cost-effective analysis of large manuscripts"
            }
        }
    
    @staticmethod
    def get_provider_strengths() -> Dict[str, List[str]]:
        """Get strengths of each provider for literary analysis."""
        return {
            "openai": [
                "Strong reasoning capabilities with o3",
                "Good instruction following",
                "Consistent analytical framework",
                "Affordable after recent price cuts"
            ],
            "anthropic": [
                "Extended thinking with Claude 3.7",
                "Nuanced literary understanding", 
                "Strong cultural and contextual awareness",
                "Excellent for sustained analysis"
            ],
            "gemini": [
                "Built-in thinking capabilities",
                "Largest context windows (1M+ tokens)",
                "Good pattern recognition",
                "Cost-effective for large texts"
            ]
        }


# Convenience function for creating providers
def create_provider(provider_type: str, model: str = None, **kwargs) -> AIProvider:
    """Create a provider with optional model auto-selection."""
    if not model:
        recommended = ProviderFactory.get_recommended_models()
        model = recommended.get(provider_type)
        if not model:
            raise ValueError(f"No recommended model for provider: {provider_type}")
    
    return ProviderFactory.create_provider(provider_type, model, **kwargs)