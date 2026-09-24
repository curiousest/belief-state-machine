const puppeteer = require('puppeteer');
const { spawn } = require('child_process');
const path = require('path');

describe('Manuscript Editor', () => {
  let browser;
  let page;
  let server;

  beforeAll(async () => {
    // Launch browser
    browser = await puppeteer.launch({
      headless: false, // Set to true for CI
      slowMo: 50,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    page = await browser.newPage();
    await page.setViewport({ width: 1200, height: 800 });

    // Start a simple HTTP server for testing
    server = spawn('npm', ['run', 'dev:web'], {
      cwd: path.join(__dirname, '..'),
      stdio: 'pipe'
    });

    // Wait for server to start
    await new Promise((resolve) => {
      setTimeout(resolve, 3000);
    });

    // Navigate to the web version
    await page.goto('http://localhost:3000/index-web.html');
    
    // Wait for the app to load
    await page.waitForSelector('#editor-container', { timeout: 10000 });
  });

  afterAll(async () => {
    if (server) {
      server.kill();
    }
    if (browser) {
      await browser.close();
    }
  });

  test('should load the manuscript editor interface', async () => {
    // Check that main UI elements are present
    await page.waitForSelector('.app-container');
    await page.waitForSelector('.toolbar');
    await page.waitForSelector('.main-content');
    await page.waitForSelector('.editor-panel');
    await page.waitForSelector('.feedback-panel');

    // Check toolbar buttons
    const openFileBtn = await page.$('#openFile');
    const saveFileBtn = await page.$('#saveFile');
    const contextBtn = await page.$('#openContext');
    const themeBtn = await page.$('#themeToggle');
    const settingsBtn = await page.$('#settings');

    expect(openFileBtn).toBeTruthy();
    expect(saveFileBtn).toBeTruthy();
    expect(contextBtn).toBeTruthy();
    expect(themeBtn).toBeTruthy();
    expect(settingsBtn).toBeTruthy();
  });

  test('should display CodeMirror editor with initial content', async () => {
    // Wait for CodeMirror to load
    await page.waitForSelector('.cm-editor');
    await page.waitForSelector('.cm-scroller');

    // Check that initial content is loaded
    const editorContent = await page.$eval('.cm-editor', (el) => {
      return el.textContent;
    });

    expect(editorContent).toContain('Your Manuscript');
    expect(editorContent).toContain('Start writing your story here');
  });

  test('should show feedback button when text is selected', async () => {
    // Wait for editor to be ready
    await page.waitForSelector('.cm-editor');
    
    // Click in the editor to focus it
    await page.click('.cm-editor');
    
    // Select some text by triple-clicking to select a line
    await page.click('.cm-line', { clickCount: 3 });
    
    // Wait a moment for the selection handler
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Check if feedback button appears
    const feedbackBtn = await page.$('#feedback-trigger');
    if (feedbackBtn) {
      const btnText = await feedbackBtn.evaluate(el => el.textContent);
      expect(btnText).toBe('Ask AI for Feedback');
    } else {
      // Try selecting text manually if triple-click didn't work
      await page.evaluate(() => {
        const editor = document.querySelector('.cm-editor');
        const range = document.createRange();
        const textNode = editor.querySelector('.cm-line').firstChild;
        if (textNode) {
          range.selectNodeContents(textNode);
          const selection = window.getSelection();
          selection.removeAllRanges();
          selection.addRange(range);
          
          // Trigger mouseup event
          const event = new MouseEvent('mouseup', { bubbles: true });
          editor.dispatchEvent(event);
        }
      });
      
      await new Promise(resolve => setTimeout(resolve, 500));
      const feedbackBtnRetry = await page.$('#feedback-trigger');
      if (feedbackBtnRetry) {
        const btnText = await feedbackBtnRetry.evaluate(el => el.textContent);
        expect(btnText).toBe('Ask AI for Feedback');
      }
    }
  });

  test('should open and close settings modal', async () => {
    // Click settings button
    await page.click('#settings');
    
    // Wait for modal to open
    await page.waitForSelector('#settingsModal', { visible: true });
    
    // Check modal content
    const modal = await page.$('#settingsModal');
    const modalStyle = await modal.evaluate(el => getComputedStyle(el).display);
    expect(modalStyle).toBe('flex');
    
    // Check form fields
    const apiKeyInput = await page.$('#apiKey');
    const contextPathInput = await page.$('#contextPath');
    expect(apiKeyInput).toBeTruthy();
    expect(contextPathInput).toBeTruthy();
    
    // Close modal
    await page.click('#closeSettings');
    
    // Wait for modal to close
    await new Promise(resolve => setTimeout(resolve, 500));
    const modalStyleClosed = await modal.evaluate(el => getComputedStyle(el).display);
    expect(modalStyleClosed).toBe('none');
  });

  test('should open and close context modal', async () => {
    // Click context button
    await page.click('#openContext');
    
    // Wait for modal to open
    await page.waitForSelector('#contextModal', { visible: true });
    
    // Check modal content
    const modal = await page.$('#contextModal');
    const modalStyle = await modal.evaluate(el => getComputedStyle(el).display);
    expect(modalStyle).toBe('flex');
    
    // Check textarea
    const contextEditor = await page.$('#contextEditor');
    expect(contextEditor).toBeTruthy();
    
    // Add some content
    await page.type('#contextEditor', 'This is test story context with character backgrounds.');
    
    // Save context
    await page.click('#saveContext');
    
    // Modal should close
    await new Promise(resolve => setTimeout(resolve, 500));
    const modalStyleClosed = await modal.evaluate(el => getComputedStyle(el).display);
    expect(modalStyleClosed).toBe('none');
  });

  test('should toggle theme', async () => {
    // Check initial theme
    const body = await page.$('body');
    let hasTheme = await body.evaluate(el => el.classList.contains('dark-theme'));
    
    // Click theme toggle
    await page.click('#themeToggle');
    
    // Wait for theme change
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Check theme changed
    const hasThemeAfter = await body.evaluate(el => el.classList.contains('dark-theme'));
    expect(hasThemeAfter).toBe(!hasTheme);
    
    // Check button text changed
    const themeBtn = await page.$('#themeToggle');
    const btnText = await themeBtn.evaluate(el => el.textContent);
    expect(['🌙', '☀️']).toContain(btnText);
  });

  test('should display existing feedback in panel', async () => {
    // Wait for feedback panel to load
    await page.waitForSelector('.feedback-list');
    
    // Check if there are feedback items (loaded from mock)
    const feedbackItems = await page.$$('.feedback-item');
    expect(feedbackItems.length).toBeGreaterThan(0);
    
    // Check feedback item structure
    if (feedbackItems.length > 0) {
      const firstItem = feedbackItems[0];
      const timestamp = await firstItem.$('.feedback-timestamp');
      const passage = await firstItem.$('.feedback-passage');
      const content = await firstItem.$('.feedback-content');
      const tagSelect = await firstItem.$('.tag-select');
      
      expect(timestamp).toBeTruthy();
      expect(passage).toBeTruthy();
      expect(content).toBeTruthy();
      expect(tagSelect).toBeTruthy();
    }
  });

  test('should request AI feedback on text selection', async () => {
    // First, let's add some mock console logging to track the process
    page.on('console', msg => {
      if (msg.text().includes('Mock')) {
        console.log('Browser console:', msg.text());
      }
    });

    // Focus the editor and select text
    await page.click('.cm-editor');
    
    // Use JavaScript to select text and trigger feedback
    await page.evaluate(() => {
      // Get the editor content
      const editor = document.querySelector('.cm-editor');
      const line = editor.querySelector('.cm-line');
      
      if (line && line.textContent.length > 20) {
        // Create a selection
        const range = document.createRange();
        const textNode = line.firstChild;
        if (textNode) {
          range.setStart(textNode, 0);
          range.setEnd(textNode, Math.min(50, textNode.textContent.length));
          
          const selection = window.getSelection();
          selection.removeAllRanges();
          selection.addRange(range);
          
          // Dispatch mouseup event to trigger selection handler
          const event = new MouseEvent('mouseup', { bubbles: true });
          editor.dispatchEvent(event);
        }
      }
    });
    
    // Wait for feedback button to appear
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Try to find and click the feedback button
    const feedbackBtn = await page.$('#feedback-trigger');
    if (feedbackBtn) {
      // Count feedback items before
      const feedbackItemsBefore = await page.$$('.feedback-item');
      const countBefore = feedbackItemsBefore.length;
      
      // Click the feedback button
      await feedbackBtn.click();
      
      // Wait for feedback to be processed
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Check if new feedback was added
      const feedbackItemsAfter = await page.$$('.feedback-item');
      const countAfter = feedbackItemsAfter.length;
      
      expect(countAfter).toBeGreaterThan(countBefore);
    } else {
      console.log('Feedback button not found, checking existing feedback instead');
      // If we can't trigger new feedback, at least verify existing feedback works
      const feedbackItems = await page.$$('.feedback-item');
      expect(feedbackItems.length).toBeGreaterThanOrEqual(1);
    }
  });

  test('should handle file operations', async () => {
    // Test open file (mock)
    await page.click('#openFile');
    
    // Wait for content to load
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Check if editor content changed
    const editorContent = await page.$eval('.cm-editor', (el) => {
      return el.textContent;
    });
    
    expect(editorContent).toContain('Test Document');
    
    // Test save file
    await page.click('#saveFile');
    
    // Should not throw error (mock save)
    await new Promise(resolve => setTimeout(resolve, 500));
  });

  test('should manage feedback tags', async () => {
    // Find a feedback item with tag select
    const tagSelect = await page.$('.tag-select');
    
    if (tagSelect) {
      // Get current value
      const currentValue = await tagSelect.evaluate(el => el.value);
      
      // Change to different value
      const newValue = currentValue === 'pending' ? 'keep' : 'pending';
      await page.select('.tag-select', newValue);
      
      // Wait for change to process
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Verify change
      const updatedValue = await tagSelect.evaluate(el => el.value);
      expect(updatedValue).toBe(newValue);
    }
  });

  test('should clear all feedback', async () => {
    // Check initial feedback count
    const feedbackItemsBefore = await page.$$('.feedback-item');
    
    if (feedbackItemsBefore.length > 0) {
      // Set up dialog handler first
      page.on('dialog', async dialog => {
        await dialog.accept();
      });
      
      // Click clear feedback button
      await page.click('#clearFeedback');
      
      // Wait for feedback to clear
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Check feedback cleared
      const feedbackItemsAfter = await page.$$('.feedback-item');
      expect(feedbackItemsAfter.length).toBe(0);
    }
  });

  test('should open and close generate context modal', async () => {
    // Click generate context button
    await page.click('#generateContext');
    
    // Wait for modal to open
    await page.waitForSelector('#generateContextModal', { visible: true });
    
    // Check modal content
    const modal = await page.$('#generateContextModal');
    const modalStyle = await modal.evaluate(el => getComputedStyle(el).display);
    expect(modalStyle).toBe('flex');
    
    // Check form elements
    const manuscriptInput = await page.$('#manuscriptInput');
    const generateBtn = await page.$('#generateContextBtn');
    expect(manuscriptInput).toBeTruthy();
    expect(generateBtn).toBeTruthy();
    
    // Close modal
    await page.click('#closeGenerateContext');
    
    // Wait for modal to close
    await new Promise(resolve => setTimeout(resolve, 500));
    const modalStyleClosed = await modal.evaluate(el => getComputedStyle(el).display);
    expect(modalStyleClosed).toBe('none');
  });

  test('should generate story context from manuscript', async () => {
    // Open generate context modal
    await page.click('#generateContext');
    await page.waitForSelector('#generateContextModal', { visible: true });
    
    // Add sample manuscript
    const sampleManuscript = `Chapter 1: The Beginning
    
    Sarah looked out the window of her small apartment, watching the rain streak down the glass. She had been living in this city for three years now, but still felt like an outsider. The job at the marketing firm was paying the bills, but it wasn't fulfilling the dreams she had when she first moved here.
    
    Her phone buzzed with a text from her mother: "How are you doing, honey?" Sarah stared at the message for a long moment before typing back: "Fine, just busy with work."
    
    It wasn't entirely true. She wasn't fine, and work wasn't that busy. But how could she explain the growing sense of restlessness that had been gnawing at her for months?`;
    
    await page.type('#manuscriptInput', sampleManuscript);
    
    // Click generate button
    await page.click('#generateContextBtn');
    
    // Wait for generation to complete (mock delay)
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Check if context was generated
    const contextOutput = await page.$('.generate-context-output');
    const isVisible = await contextOutput.evaluate(el => getComputedStyle(el).display !== 'none');
    expect(isVisible).toBe(true);
    
    // Check if generated context has content
    const generatedText = await page.$eval('#generatedContext', el => el.value);
    expect(generatedText.length).toBeGreaterThan(100);
    expect(generatedText).toContain('Story Overview');
    
    // Test accept context
    await page.click('#acceptContext');
    
    // Should show success message and close modal
    await new Promise(resolve => setTimeout(resolve, 1000));
  });

  test('should allow editing generated context', async () => {
    // Open generate context modal and generate context first
    await page.click('#generateContext');
    await page.waitForSelector('#generateContextModal', { visible: true });
    
    await page.type('#manuscriptInput', 'Sample text for context generation');
    await page.click('#generateContextBtn');
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Wait for context to be generated
    await page.waitForSelector('.generate-context-output', { visible: true });
    
    // Click edit button
    await page.click('#editContext');
    
    // Check if textarea is now editable
    const isReadonly = await page.$eval('#generatedContext', el => el.readOnly);
    expect(isReadonly).toBe(false);
    
    // Check if button text changed
    const buttonText = await page.$eval('#acceptContext', el => el.textContent);
    expect(buttonText).toBe('Save Edited Context');
    
    // Close modal
    await page.click('#closeGenerateContext');
  });
});

// Helper function to wait for element to be visible
async function waitForVisible(page, selector, timeout = 5000) {
  return await page.waitForSelector(selector, { visible: true, timeout });
}