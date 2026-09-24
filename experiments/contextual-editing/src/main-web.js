import { EditorView, basicSetup } from "codemirror";
import { markdown } from "@codemirror/lang-markdown";
import { oneDark } from "@codemirror/theme-one-dark";
import { EditorState } from "@codemirror/state";

// Mock Tauri APIs for web testing
const mockTauri = {
  invoke: async (command, args) => {
    console.log('Mock Tauri invoke:', command, args);
    
    switch (command) {
      case 'read_config':
        return {
          openai_api_key: 'mock-api-key',
          context_file_path: 'story_context.md',
          theme: 'light'
        };
      case 'save_config':
        return true;
      case 'read_file':
        if (args.path === 'story_context.md') {
          return 'This is a mock story context file with character backgrounds and themes.';
        }
        return 'Mock file content';
      case 'write_file':
        return true;
      case 'save_feedback':
        return true;
      case 'load_feedback':
        return [
          {
            id: '1',
            passage: 'Sample passage for testing',
            context: 'Mock context around the passage',
            feedback: 'This is mock AI feedback for testing purposes.',
            timestamp: new Date().toISOString(),
            tag: 'pending'
          }
        ];
      default:
        return null;
    }
  }
};

const mockDialog = {
  open: async () => null,
  save: async () => null
};

// Mock OpenAI for testing
class MockOpenAI {
  constructor(config) {
    this.apiKey = config.apiKey;
  }
  
  chat = {
    completions: {
      create: async (params) => {
        return {
          choices: [{
            message: {
              content: `Mock AI feedback for the passage. This would normally provide editorial feedback on tone, clarity, structure, emotional rhythm, and pacing based on the story context and surrounding text.

The selected text shows good narrative flow but could benefit from stronger sensory details to ground the reader in the scene.`
            }
          }]
        };
      }
    }
  };
}

// Replace global objects for web testing
window.__TAURI__ = { tauri: mockTauri, dialog: mockDialog };
window.OpenAI = MockOpenAI;

class ManuscriptEditor {
  constructor() {
    this.editor = null;
    this.currentFile = null;
    this.config = null;
    this.openai = null;
    this.feedback = [];
    this.isDark = false;
    
    this.init();
  }

  async init() {
    await this.loadConfig();
    this.setupEditor();
    this.setupEventListeners();
    await this.loadFeedback();
    this.updateTheme();
  }

  async loadConfig() {
    try {
      this.config = await mockTauri.invoke("read_config");
      if (this.config.openai_api_key) {
        this.openai = new MockOpenAI({
          apiKey: this.config.openai_api_key
        });
      }
      this.isDark = this.config.theme === "dark";
    } catch (error) {
      console.error("Failed to load config:", error);
      this.config = {
        openai_api_key: "mock-key",
        context_file_path: "story_context.md",
        theme: "light"
      };
    }
  }

  setupEditor() {
    const extensions = [
      basicSetup,
      markdown(),
      EditorView.theme({
        "&": { height: "100%" },
        ".cm-scroller": { fontFamily: "Georgia, serif", fontSize: "16px", lineHeight: "1.6" },
        ".cm-focused": { outline: "none" }
      })
    ];

    if (this.isDark) {
      extensions.push(oneDark);
    }

    this.editor = new EditorView({
      state: EditorState.create({
        doc: "# Your Manuscript\n\nStart writing your story here... This is a test passage that we can select to get AI feedback. The editor should allow text selection and show a feedback button when text is selected.",
        extensions
      }),
      parent: document.getElementById("editor-container")
    });

    // Add selection listener for feedback button
    this.editor.dom.addEventListener("mouseup", () => {
      this.handleTextSelection();
    });
  }

  handleTextSelection() {
    const selection = this.editor.state.selection.main;
    if (!selection.empty) {
      const selectedText = this.editor.state.doc.sliceString(selection.from, selection.to);
      if (selectedText.trim().length > 10) {
        this.showFeedbackButton(selection, selectedText);
      }
    } else {
      this.hideFeedbackButton();
    }
  }

  showFeedbackButton(selection, selectedText) {
    this.hideFeedbackButton();
    
    const button = document.createElement("button");
    button.className = "feedback-trigger-btn";
    button.textContent = "Ask AI for Feedback";
    button.id = "feedback-trigger";
    button.onclick = () => this.requestFeedback(selectedText, selection);
    
    // Position button near selection
    const coords = this.editor.coordsAtPos(selection.from);
    if (coords) {
      button.style.position = "absolute";
      button.style.left = coords.left + "px";
      button.style.top = (coords.top - 35) + "px";
      button.style.zIndex = "1000";
      
      document.body.appendChild(button);
    }
  }

  hideFeedbackButton() {
    const existingBtn = document.querySelector(".feedback-trigger-btn");
    if (existingBtn) {
      existingBtn.remove();
    }
  }

  async generateStoryContext(manuscriptText) {
    if (!this.openai) {
      throw new Error("Please configure your OpenAI API key in settings.");
    }

    // Mock response for testing
    const mockContext = `# Story Context Summary

## Story Overview
**Genre**: Literary Fiction with Philosophical Elements
**Tone**: Contemplative, introspective, with moments of dark humor
**Setting**: Contemporary urban setting, primarily in a mid-sized city
**Time Period**: Present day
**Central Themes**: Identity, purpose, human connection, the search for meaning

## Main Characters
**Protagonist**: A reflective individual grappling with existential questions and personal relationships
**Supporting Characters**: Various individuals who represent different life philosophies and approaches to existence

## Plot Structure
- **Opening**: Establishment of the protagonist's internal conflict
- **Rising Action**: Encounters with different perspectives and life situations
- **Climax**: A moment of realization or confrontation with core beliefs
- **Resolution**: Integration of new understanding into the character's worldview

## Themes & Motifs
- **Primary Themes**: The search for authentic existence, the role of choice in defining identity
- **Recurring Motifs**: Mirrors/reflection, journeys (both literal and metaphorical), conversations as turning points
- **Symbols**: Light and shadow as representations of clarity and confusion

## Voice & Style
**Narrative Voice**: First person or close third person, intimate and philosophical
**Writing Style**: Lyrical prose with philosophical underpinnings, careful attention to internal monologue
**Unique Elements**: Blend of everyday observations with profound insights

## World/Setting Details
**Primary Locations**: Urban environments that serve as backdrops for internal exploration
**Cultural Context**: Contemporary society with its pressures and expectations
**Atmosphere**: Realistic with moments of heightened emotional and philosophical intensity

## Theological/Philosophical Framework
**Core Philosophy**: Humanistic exploration of meaning-making and authentic living
**Spiritual Elements**: Questions of purpose and transcendence without dogmatic answers
**Ethical Considerations**: How individual choices affect both self and others

## Narrative Techniques
**POV**: Intimate perspective allowing deep character exploration
**Structure**: Character-driven with episodic elements that build toward greater understanding
**Pacing**: Contemplative, allowing time for reflection and development of ideas

*This context was generated from the full manuscript and will inform all future editorial feedback.*`;

    return mockContext;
  }

  async requestFeedback(selectedText, selection) {
    if (!this.openai) {
      alert("Please configure your OpenAI API key in settings.");
      return;
    }

    this.hideFeedbackButton();
    
    try {
      // Get surrounding context
      const doc = this.editor.state.doc;
      const contextStart = Math.max(0, selection.from - 500);
      const contextEnd = Math.min(doc.length, selection.to + 500);
      const context = doc.sliceString(contextStart, contextEnd);
      
      // Load story context
      let storyContext = "";
      try {
        storyContext = await mockTauri.invoke("read_file", { path: this.config.context_file_path });
      } catch (error) {
        console.warn("No story context file found");
      }

      const response = await this.openai.chat.completions.create({
        model: "gpt-4",
        messages: [
          { role: "system", content: `Story Context: ${storyContext}\n\nSurrounding Context: ${context}` },
          { role: "user", content: `Please provide feedback on this passage:\n\n${selectedText}` }
        ],
        max_tokens: 1000
      });

      const feedback = response.choices[0].message.content;
      
      // Save feedback
      const feedbackEntry = {
        id: Date.now().toString(),
        passage: selectedText,
        context: context,
        feedback: feedback,
        timestamp: new Date().toISOString(),
        tag: "pending"
      };

      await mockTauri.invoke("save_feedback", { feedback: feedbackEntry });
      this.feedback.push(feedbackEntry);
      this.renderFeedback();

    } catch (error) {
      console.error("Error requesting feedback:", error);
      alert("Failed to get AI feedback. Please check your API key and connection.");
    }
  }

  async loadFeedback() {
    try {
      this.feedback = await mockTauri.invoke("load_feedback");
      this.renderFeedback();
    } catch (error) {
      console.error("Failed to load feedback:", error);
      this.feedback = [];
    }
  }

  renderFeedback() {
    const feedbackList = document.getElementById("feedback-list");
    feedbackList.innerHTML = "";

    this.feedback.forEach(entry => {
      const feedbackItem = document.createElement("div");
      feedbackItem.className = "feedback-item";
      feedbackItem.innerHTML = `
        <div class="feedback-header">
          <span class="feedback-timestamp">${new Date(entry.timestamp).toLocaleString()}</span>
          <div class="feedback-tags">
            <select class="tag-select" data-id="${entry.id}">
              <option value="pending" ${entry.tag === "pending" ? "selected" : ""}>Pending</option>
              <option value="keep" ${entry.tag === "keep" ? "selected" : ""}>Keep</option>
              <option value="resolved" ${entry.tag === "resolved" ? "selected" : ""}>Resolved</option>
              <option value="dismissed" ${entry.tag === "dismissed" ? "selected" : ""}>Dismissed</option>
              <option value="follow-up" ${entry.tag === "follow-up" ? "selected" : ""}>Follow-up</option>
            </select>
            <button class="delete-feedback" data-id="${entry.id}">×</button>
          </div>
        </div>
        <div class="feedback-passage">"${entry.passage.substring(0, 100)}${entry.passage.length > 100 ? "..." : ""}"</div>
        <div class="feedback-content">${entry.feedback}</div>
      `;
      feedbackList.appendChild(feedbackItem);
    });

    // Add event listeners for tags and delete buttons
    document.querySelectorAll(".tag-select").forEach(select => {
      select.addEventListener("change", (e) => {
        this.updateFeedbackTag(e.target.dataset.id, e.target.value);
      });
    });

    document.querySelectorAll(".delete-feedback").forEach(button => {
      button.addEventListener("click", (e) => {
        this.deleteFeedback(e.target.dataset.id);
      });
    });
  }

  updateFeedbackTag(id, tag) {
    const entry = this.feedback.find(f => f.id === id);
    if (entry) {
      entry.tag = tag;
    }
  }

  deleteFeedback(id) {
    this.feedback = this.feedback.filter(f => f.id !== id);
    this.renderFeedback();
  }

  setupEventListeners() {
    // File operations
    document.getElementById("openFile").addEventListener("click", async () => {
      // Mock file opening for testing
      const content = "# Test Document\n\nThis is a test document loaded from a file. You can select text here to test the AI feedback functionality.";
      this.editor.dispatch({
        changes: { from: 0, to: this.editor.state.doc.length, insert: content }
      });
      this.currentFile = "test-document.md";
    });

    document.getElementById("saveFile").addEventListener("click", async () => {
      try {
        const content = this.editor.state.doc.toString();
        await mockTauri.invoke("write_file", { path: this.currentFile || "test-document.md", content });
        console.log("File saved successfully");
      } catch (error) {
        alert("Failed to save file: " + error);
      }
    });

    // Context modal
    document.getElementById("openContext").addEventListener("click", () => {
      document.getElementById("contextModal").style.display = "flex";
      this.loadContextFile();
    });

    document.getElementById("closeContext").addEventListener("click", () => {
      document.getElementById("contextModal").style.display = "none";
    });

    document.getElementById("saveContext").addEventListener("click", async () => {
      const content = document.getElementById("contextEditor").value;
      try {
        await mockTauri.invoke("write_file", { path: this.config.context_file_path, content });
        document.getElementById("contextModal").style.display = "none";
      } catch (error) {
        alert("Failed to save context: " + error);
      }
    });

    // Settings modal
    document.getElementById("settings").addEventListener("click", () => {
      document.getElementById("settingsModal").style.display = "flex";
      document.getElementById("apiKey").value = this.config.openai_api_key || "";
      document.getElementById("contextPath").value = this.config.context_file_path || "";
    });

    document.getElementById("closeSettings").addEventListener("click", () => {
      document.getElementById("settingsModal").style.display = "none";
    });

    document.getElementById("saveSettings").addEventListener("click", async () => {
      this.config.openai_api_key = document.getElementById("apiKey").value;
      this.config.context_file_path = document.getElementById("contextPath").value;
      
      try {
        await mockTauri.invoke("save_config", { config: this.config });
        if (this.config.openai_api_key) {
          this.openai = new MockOpenAI({
            apiKey: this.config.openai_api_key
          });
        }
        document.getElementById("settingsModal").style.display = "none";
      } catch (error) {
        alert("Failed to save settings: " + error);
      }
    });

    // Theme toggle
    document.getElementById("themeToggle").addEventListener("click", () => {
      this.isDark = !this.isDark;
      this.config.theme = this.isDark ? "dark" : "light";
      this.updateTheme();
      mockTauri.invoke("save_config", { config: this.config });
    });

    // Clear feedback
    document.getElementById("clearFeedback").addEventListener("click", () => {
      if (confirm("Clear all feedback? This cannot be undone.")) {
        this.feedback = [];
        this.renderFeedback();
        mockTauri.invoke("write_file", { path: "feedback.json", content: "[]" });
      }
    });

    // Generate context modal
    document.getElementById("generateContext").addEventListener("click", () => {
      document.getElementById("generateContextModal").style.display = "flex";
      document.getElementById("manuscriptInput").value = "";
      document.querySelector(".generate-context-output").style.display = "none";
      document.getElementById("generatedContext").value = "";
    });

    document.getElementById("closeGenerateContext").addEventListener("click", () => {
      document.getElementById("generateContextModal").style.display = "none";
    });

    document.getElementById("cancelGenerate").addEventListener("click", () => {
      document.getElementById("generateContextModal").style.display = "none";
    });

    document.getElementById("generateContextBtn").addEventListener("click", async () => {
      const manuscriptText = document.getElementById("manuscriptInput").value.trim();
      
      if (!manuscriptText) {
        alert("Please paste your manuscript text first.");
        return;
      }

      if (!this.openai) {
        alert("Please configure your OpenAI API key in settings first.");
        return;
      }

      try {
        // Show loading state
        const btnText = document.querySelector("#generateContextBtn .btn-text");
        const btnLoading = document.querySelector("#generateContextBtn .btn-loading");
        const generateBtn = document.getElementById("generateContextBtn");
        
        generateBtn.disabled = true;
        btnText.style.display = "none";
        btnLoading.style.display = "inline";

        // Generate context (mock delay)
        await new Promise(resolve => setTimeout(resolve, 2000));
        const generatedContext = await this.generateStoryContext(manuscriptText);
        
        // Show results
        document.getElementById("generatedContext").value = generatedContext;
        document.querySelector(".generate-context-output").style.display = "block";
        
        // Reset button state
        generateBtn.disabled = false;
        btnText.style.display = "inline";
        btnLoading.style.display = "none";

      } catch (error) {
        console.error("Error generating context:", error);
        alert("Failed to generate story context: " + error.message);
        
        // Reset button state
        const btnText = document.querySelector("#generateContextBtn .btn-text");
        const btnLoading = document.querySelector("#generateContextBtn .btn-loading");
        const generateBtn = document.getElementById("generateContextBtn");
        
        generateBtn.disabled = false;
        btnText.style.display = "inline";
        btnLoading.style.display = "none";
      }
    });

    document.getElementById("acceptContext").addEventListener("click", async () => {
      const generatedContext = document.getElementById("generatedContext").value;
      try {
        await mockTauri.invoke("write_file", { path: this.config.context_file_path, content: generatedContext });
        alert("Story context saved successfully! This will now be used for all future feedback.");
        document.getElementById("generateContextModal").style.display = "none";
      } catch (error) {
        alert("Failed to save context: " + error);
      }
    });

    document.getElementById("editContext").addEventListener("click", () => {
      document.getElementById("generatedContext").readOnly = false;
      document.getElementById("generatedContext").focus();
      
      // Change button text to indicate editing mode
      document.getElementById("acceptContext").textContent = "Save Edited Context";
    });
  }

  async loadContextFile() {
    try {
      const content = await mockTauri.invoke("read_file", { path: this.config.context_file_path });
      document.getElementById("contextEditor").value = content;
    } catch (error) {
      document.getElementById("contextEditor").value = "";
    }
  }

  updateTheme() {
    const themeButton = document.getElementById("themeToggle");
    if (this.isDark) {
      document.body.classList.add("dark-theme");
      themeButton.textContent = "☀️";
    } else {
      document.body.classList.remove("dark-theme");
      themeButton.textContent = "🌙";
    }
    
    // Recreate editor with new theme
    if (this.editor) {
      const content = this.editor.state.doc.toString();
      this.editor.destroy();
      this.setupEditor();
      this.editor.dispatch({
        changes: { from: 0, to: this.editor.state.doc.length, insert: content }
      });
    }
  }
}

// Initialize the app
new ManuscriptEditor();