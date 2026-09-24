import { invoke } from "@tauri-apps/api/tauri";
import { open, save } from "@tauri-apps/api/dialog";
import { EditorView, basicSetup } from "codemirror";
import { markdown } from "@codemirror/lang-markdown";
import { oneDark } from "@codemirror/theme-one-dark";
import { EditorState } from "@codemirror/state";
import OpenAI from "openai";

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
      this.config = await invoke("read_config");
      if (this.config.openai_api_key) {
        this.openai = new OpenAI({
          apiKey: this.config.openai_api_key,
          dangerouslyAllowBrowser: true
        });
      }
      this.isDark = this.config.theme === "dark";
    } catch (error) {
      console.error("Failed to load config:", error);
      this.config = {
        openai_api_key: "",
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
        doc: "# Your Manuscript\n\nStart writing your story here...",
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

    const systemPrompt = `You are a development editor tasked with creating a comprehensive story context summary. 

Analyze the complete manuscript provided and create a detailed story context that will be used to inform future editorial feedback. Your output will be saved as the global story context and used for all subsequent feedback sessions WITHOUT the full manuscript text.

Create a comprehensive summary that includes:

1. **Story Overview**: Genre, tone, setting, time period, and central themes
2. **Main Characters**: Key characters with their roles, motivations, and character arcs
3. **Plot Structure**: Major plot points, conflicts, and story progression
4. **Themes & Motifs**: Central themes, symbols, and recurring elements
5. **Voice & Style**: Narrative voice, writing style, and unique elements
6. **World/Setting Details**: Important locations, cultural context, rules of the world
7. **Theological/Philosophical Framework**: If applicable, any spiritual or philosophical themes
8. **Narrative Techniques**: POV, structure, pacing patterns

Be thorough and specific - this context will guide all future feedback without access to the full text. Focus on elements that would help an editor understand the story's essence, characters, and artistic vision.`;

    const response = await this.openai.chat.completions.create({
      model: "gpt-4",
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: `Please analyze this complete manuscript and create a comprehensive story context:\n\n${manuscriptText}` }
      ],
      max_tokens: 2000,
      temperature: 0.3
    });

    return response.choices[0].message.content;
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
        storyContext = await invoke("read_file", { path: this.config.context_file_path });
      } catch (error) {
        console.warn("No story context file found");
      }

      const systemPrompt = `You are a development editor. First, read the global story context provided. Then read the excerpt. Give constructive feedback on tone, clarity, structure, emotional rhythm, and pacing. Provide optional rewrite suggestions only if useful. Do not make any edits—this is a read-only advisory role.

Story Context:
${storyContext}

Surrounding Context:
${context}`;

      const response = await this.openai.chat.completions.create({
        model: "gpt-4",
        messages: [
          { role: "system", content: systemPrompt },
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

      await invoke("save_feedback", { feedback: feedbackEntry });
      this.feedback.push(feedbackEntry);
      this.renderFeedback();

    } catch (error) {
      console.error("Error requesting feedback:", error);
      alert("Failed to get AI feedback. Please check your API key and connection.");
    }
  }

  async loadFeedback() {
    try {
      this.feedback = await invoke("load_feedback");
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
      // In a real app, you'd save this back to the file
    }
  }

  deleteFeedback(id) {
    this.feedback = this.feedback.filter(f => f.id !== id);
    this.renderFeedback();
    // In a real app, you'd save this back to the file
  }

  setupEventListeners() {
    // File operations
    document.getElementById("openFile").addEventListener("click", async () => {
      const selected = await open({
        filters: [
          { name: "Markdown", extensions: ["md", "markdown"] },
          { name: "Text", extensions: ["txt"] }
        ]
      });
      
      if (selected) {
        try {
          const content = await invoke("read_file", { path: selected });
          this.editor.dispatch({
            changes: { from: 0, to: this.editor.state.doc.length, insert: content }
          });
          this.currentFile = selected;
        } catch (error) {
          alert("Failed to open file: " + error);
        }
      }
    });

    document.getElementById("saveFile").addEventListener("click", async () => {
      if (!this.currentFile) {
        const selected = await save({
          filters: [
            { name: "Markdown", extensions: ["md"] },
            { name: "Text", extensions: ["txt"] }
          ]
        });
        if (selected) {
          this.currentFile = selected;
        } else {
          return;
        }
      }

      try {
        const content = this.editor.state.doc.toString();
        await invoke("write_file", { path: this.currentFile, content });
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
        await invoke("write_file", { path: this.config.context_file_path, content });
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
        await invoke("save_config", { config: this.config });
        if (this.config.openai_api_key) {
          this.openai = new OpenAI({
            apiKey: this.config.openai_api_key,
            dangerouslyAllowBrowser: true
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
      invoke("save_config", { config: this.config });
    });

    // Clear feedback
    document.getElementById("clearFeedback").addEventListener("click", () => {
      if (confirm("Clear all feedback? This cannot be undone.")) {
        this.feedback = [];
        this.renderFeedback();
        invoke("write_file", { path: "feedback.json", content: "[]" });
      }
    });

    // Generate context modal
    document.getElementById("generateContext").addEventListener("click", () => {
      document.getElementById("generateContextModal").style.display = "flex";
      document.getElementById("manuscriptInput").value = "";
      document.getElementById("generate-context-output").style.display = "none";
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

        // Generate context
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
        await invoke("write_file", { path: this.config.context_file_path, content: generatedContext });
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
      const content = await invoke("read_file", { path: this.config.context_file_path });
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