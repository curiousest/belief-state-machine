"""
Prompt configurations for literary analysis.
Centralized location for all analysis prompts and categories.
"""

from typing import List, Tuple, Dict
from dataclasses import dataclass


@dataclass
class PromptCategory:
    """A category of related prompts."""
    name: str
    description: str
    prompts: List[Tuple[str, str]]  # (filename, prompt_text)


class PromptLibrary:
    """Library of all analysis prompts organized by category."""

    @property
    def chapter_analysis_prompts(self) -> List[Tuple[str, str]]:
        """Prompts for individual chapter analysis."""
        return [
            (
                "character_analysis.txt",
                "Do the characters feel psychologically real and internally consistent? Are their motivations emotionally resonant and their transformations earned, or do they veer into abstraction?"
            ),
            (
                "dialogue_evaluation.txt",
                "Evaluate the dialogue in this story. Does it feel alive and distinct between characters, or does it flatten into exposition, shared cadence, or writerly voice?"
            ),
            (
                "pacing_analysis.txt",
                "Describe the pacing of this story. How does the rhythm of scenes shape the reader’s emotional and narrative momentum? Where does it build tension, and where might it stall or dissipate?"
            ),
            (
                "complexity_balance.txt",
                "Does this story balance complexity and clarity? Identify moments where philosophical content becomes dense, disorienting, or self-referential. How might clarity be restored without flattening the work’s depth?"
            ),
            (
                "central_tension.txt",
                "What is the central emotional or philosophical tension in this story? Is it dramatized through conflict, subtext, or emotional stakes, or is it stated more than embodied?"
            ),
            (
                "narrative_function.txt",
                "Does this chapter hold narrative weight on its own while deepening the manuscript’s overarching arc, theme, or character journey?"
            ),
            (
                "scene_structure.txt",
                "Which scenes could be cut, condensed, or expanded to heighten emotional momentum, thematic clarity, or structural rhythm?"
            )
        ]

    @property
    def transition_analysis_prompts(self) -> List[Tuple[str, str]]:
        """Prompts for analyzing transitions between chapters."""
        return [
            (
                "transition_flow.txt",
                "Does the transition between these two stories feel abrupt or disorienting? What might help reorient the reader without reducing the stylistic or conceptual ambition?"
            ),
            (
                "transition_connections.txt",
                "What formal, emotional, or thematic threads link these two stories? Could those connections be made more legible or felt?"
            ),
            (
                "transition_progression.txt",
                "Does the second story evolve or echo the emotional or philosophical terrain of the first, or does it reset too sharply?"
            )
        ]

    @property
    def holistic_analysis_prompts(self) -> List[Tuple[str, str]]:
        """Prompts for full manuscript analysis."""
        return [
            (
                "structure_division_meaning.txt",
                "How do the manuscript’s formal choices—its division into 7 stories, ordering, recursive elements—shape its philosophical or emotional resonance?"
            ),
            (
                "structure_cohesion.txt",
                "Does the manuscript function both as a collection of individual stories and as a single cohesive work? Where does the integration succeed or falter, and why?"
            ),
            (
                "structure_risks.txt",
                "What are the structural risks the manuscript takes (e.g., nonlinear sequence, nested references, abrupt shifts)? Do these risks invite richer interpretation, or do they risk reader alienation?"
            ),
            (
                "themes_embodiment.txt",
                "Identify the primary philosophical themes explored across the manuscript (e.g., identity, memory, consciousness, simulation). How do story, image, or character enact the themes, rather than simply state or theorize them?"
            ),
            (
                "themes_coherence.txt",
                "Are the themes coherent across stories, or do they diverge or contradict in ways that feel accidental, generative, or in need of resolution?"
            ),
            (
                "themes_resonance.txt",
                "Which moments or stories feel the most philosophically rich or resonant? Which feel least integrated or impactful, and why?"
            ),
            (
                "character_consistency.txt",
                "Are recurring characters internally consistent in tone, motivation, and belief? Do they evolve in surprising but coherent ways across stories? Do any feel static or discontinuous?"
            ),
            (
                "tone_shifts.txt",
                "Describe the tonal and stylistic shifts across the seven stories. Do these shifts feel intentional and enriching, or disjointed and fragmentary?"
            ),
            (
                "voice_distinctiveness.txt",
                "Is the narrative voice distinctive and deliberate? Are there places where it slips into abstraction, explanation, or monologue at the expense of narrative vividness?"
            ),
            (
                "reader_interpretation.txt",
                "What kind of interpretive work is expected of the reader? Is that work rewarded through emotional payoff, formal pattern, or unexpected structural insight?"
            ),
            (
                "reader_ambiguity.txt",
                "Does the manuscript offer meaningful ambiguity, or are there parts that may confuse or frustrate readers without yielding interpretive or emotional reward?"
            ),
            (
                "agent_perspective.txt",
                "Simulate a thoughtful literary agent reading this manuscript. Would they be intrigued by its ambition and conceptual risk, or deterred by its abstraction, length, or lack of accessibility?"
            ),
            (
                "revision_opportunities.txt",
                "What are the top three revision opportunities that could make the manuscript more emotionally resonant or structurally satisfying without compromising its ambition, voice, or philosophical subtlety?"
            ),
            (
                "best_section_analysis.txt",
                "Which individual story or section best represents the manuscript's artistic and philosophical power? What narrative, stylistic, or thematic choices make it stand out?"
            )
        ]
    
    @property
    def all_categories(self) -> Dict[str, PromptCategory]:
        """Get all prompt categories."""
        return {
            "chapter": PromptCategory(
                name="Chapter Analysis",
                description="Individual chapter/story analysis prompts",
                prompts=self.chapter_analysis_prompts
            ),
            "transition": PromptCategory(
                name="Transition Analysis", 
                description="Chapter-to-chapter transition analysis prompts",
                prompts=self.transition_analysis_prompts
            ),
            "holistic": PromptCategory(
                name="Holistic Analysis",
                description="Full manuscript analysis prompts",
                prompts=self.holistic_analysis_prompts
            )
        }
    
    def get_prompts_by_category(self, category: str) -> List[Tuple[str, str]]:
        """Get prompts for a specific category."""
        categories = self.all_categories
        if category not in categories:
            raise ValueError(f"Unknown category: {category}. Available: {list(categories.keys())}")
        return categories[category].prompts
    
    def get_custom_prompts(self, prompt_names: List[str]) -> List[Tuple[str, str]]:
        """Get specific prompts by name across all categories."""
        all_prompts = {}
        for category in self.all_categories.values():
            for name, prompt in category.prompts:
                all_prompts[name] = prompt
        
        result = []
        for name in prompt_names:
            if name not in all_prompts:
                raise ValueError(f"Unknown prompt: {name}")
            result.append((name, all_prompts[name]))
        
        return result


# Convenience instance
prompt_library = PromptLibrary()