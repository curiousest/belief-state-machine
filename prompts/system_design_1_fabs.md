You are a philosopher and literary scholar and propagadist who extracts the beliefs expressed in text.
Here are the kinds of beliefs: facts, fact assumptions, first-order beliefs, next-order beliefs, root beliefs.

Facts: explicit assertions about the real world at the time of the content. Ex: the author is from a country called Canada. The author bought a coffee today.
Fact assumptions: basic assumptions that are necessary for facts to be true. These are generally boring and not useful. Ex: there exists a country called Canada. Regions of the world can be divided into countries.
First-order beliefs: propositions immediately derivative from the content, without intermediary beliefs. Ex: learning to accept friction and flaws in oneself will bring personal growth.
Next-order beliefs: propositions that the first-order or other next-order beliefs depend upon to be true. Each layer of next-order beliefs are derived from the one previous layer and not layers beyond it. Ex: understanding oneself is essential to meaningful relationships and personal growth.
Root beliefs: next-order propositions that form a cycle in belief dependencies.

Here is the text. Next we will be extracting these beliefs from the text with specific prompts.

---

Derive optimization objectives from all this. Decide on properties of the optimization objectives (the function on it - relu, etc.):
- "Avoid 0" or "Aim for 1"?
- Priority/importance (maybe integrate this into the function - higher priority vary more)

---

Example decision with context. Compare vanilla text vs. beliefs and optimization objectives explicit.

---

Example belief-changing story with context. Compare vanilla text vs. beliefs and optimization objectives explicit.

---

Try with conversation. Try with essay.

---

This mirrors a neural network. What if we use this kind of neural network in a transformer to make the next decision for a given agent?
What does the transformer look like, made of this? What is a token, here?

---

You are a software engineer. We are building a system with the following features:
- provided a body of text and background on the author, extract the beliefs expressed in the text
- allow the user to choose whether to change or reinforce a belief
- generate a parable that changes or reinforces the belief

The system should be interactive, ideally a chat interface webapp.
The system will use crewAI+OpenAI to extract beliefs and generate parables.
The system should use django-rest-framework for the API, gcp for the backend, and react for the frontend.
A chat framework for both the frontend and backend should be used.
The system should use github actions for CI/CD, docker for containerization, terraform for deployment to gcp.
The system should be runnable and testable locally.

Recommend a system design and architecture.
Implement the local runnable system.

---

Add tests and ci/cd integration.
Explain what variables need to be manually entered in github actions.

---

Add a way to deploy the system to gcp through the ci/cd pipeline using terraform.
Explain what data needs to be manually entered in gcp and github actions.
