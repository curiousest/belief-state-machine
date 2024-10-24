You are a software engineer and machine learning engineer and data scientist designing a system with me.

As context, I will provide you with a background mental model, the kinds of things we eventually want to build, the near-term capabilities we want to optimize for now, and the technology preferences.

Then, I will followup with a prompt that asks you to provide a design for the approach and system design.

---

Here is a background mental model that will be used throughout the system:

A *belief* is a proposition you could hold to be true. An *active belief* is one you hold to be true right now. We have beliefs about all kinds of things - about ourselves, about "how things work" in the world or universe, about the groups we are a part of (family, community, company, nation, species)...

Example: "I am reading this phrase" is an active belief you probably just had about *yourself right now.

- To *have* a belief, you must remember what it feels like for it to be true.
- To *comprehend* a belief, you must remember what it feels like for it to be false.
- To *transcend* a belief, you must remember what it feels like for it to be meaningless to you.

Any belief that you can have, can also be true, false, or meaningless to you. *Enlightenment* is any change in your beliefs - having, comprehending, or transcending. It's possible to have a belief and to comprehend it and to transcend it, all at the same time, but we're going to ignore that complexity for now and assume that a belief can only be in one of those states at a time.

You can be either aware or unaware of a belief. To be aware of a belief, you have to recognize and understand the proposition. Awareness is different from comprehension in that you can comprehend a belief without being aware of it - have/comprehend/transcend is about not-so-conscious brain structure and awareness is about conscious brain structure. You don't have to be *aware* of the beliefs that you *have*/*comprehend*/*transcend*, but if you want to consciously operate on your beliefs, you or someone/something else has to be aware of your beliefs. Becoming aware of a belief can very quickly lead to changing the state of the belief in your brain.

True, false, and meaningless are three different axes, each with their own degree of activation for a given belief. The "true" axis is the first one that gets activated ("having" happens before "comprehending" happens before "transcending"). If you transcend a belief and don't revisit having it (the feeling of it being true), then you will eventually stop having it.

Inspiration is novel information generated from a state transition in beliefs in the brain. Meaning is the feeling that comes from achieving an optimization objective. Optimization objectives are abstractions to represent the things that brains use to fill in the data needed to make decisions, and optimization objectives directly result from beliefs (ex: I must constantly breathe to survive + I need to have air to breathe => always have air). Beliefs being "meaningless" means they exist, but contribute very little to optimization objectives (so the belief contributes little to any feelings of meaning). Have/comprehend/transcend are rough boundaries for different stages of a belief contributing less and less to optimization objectives over time. Beliefs contribute more to optimization objectives by having more other beliefs depend on it (ex: a higher salary for the same job is better + it's better for a child not to suffer too much => there is such a thing as "better and worse").

Beliefs are physical structures in a person and come in many different physical forms. The words "belief", "true", "false", "meaningless", and "belief spectrum" here are abstractions that encompass those structures so we can reason about things in this space - we can't express beliefs in words perfectly, but we can get close enough to make use of *all this*. This mental model is a specific kind of ontology. It's purpose is to model a state machine close to how brains work with respect to beliefs, so that we can model and operate on brains through computation on the state machine.

When extracting and representing the beliefs, those representations will trend towards the beliefs of the model used to extract/change the beliefs. Any system that operates on beliefs should support different models, so a user can choose the "universe" of belief systems they want operating on them.

Generally, beliefs trend towards becoming more false/meaningless over time, to reflect reality. There are two ways to create a new belief or make a belief more true. The first is simulation - you have to simulate the behaviour that assumes the belief to be true. The more the behaviour is simulated and the less the belief is brought into your awareness, the more the belief will become more "true" in your brain. The second is inspiration - you need to have an experience that is unexplainable using your current beliefs and fill that unknown with a new belief (you have to be confused to be inspired).

---

Here are the kinds of things we eventually want to build for our system:

Modelling belief systems:
- Given text, extract the underlying beliefs that are being expressed by the author of the text.
- Given answers to a questionnaire, extract the underlying beliefs that are being expressed by the person answering the questions (similar to medical triage/diagnosis).
- Compare two belief systems and explain the differences.
- Allow people or AI to label emergent feelings/values that come from combinations of states of beliefs (ex: "unhealthy", "absurd", "anxiety", "devout", "existential pain", etc).

Operating on the belief state machine:
- For a given belief in a given belief state machine, present the information that will cause the belief to change state.
- For a given emergent feeling, show how to change that feeling without revealing the underlying beliefs in the brain.

Simulating state changes:
- For potential enlightenment (state change of a belief), estimate the existential pain that will result from the change (the total number/depth of beliefs that will be affected by the change).
- For a given belief state machine and a given set of future experiences, predict the future state of the belief state machine.

Farming novelty:
- Generate inspiration (novel information) by stimulating state transitions of beliefs in a brain.

---

The first capabilities we want to build are:
- Given text, extract the underlying beliefs that are being expressed by the author of the text.
- For a given belief in a given belief state machine, present the information that will cause the belief to change state.

To extract the underlying beliefs that are being expressed by the author of the text, we need to do the following:
- Train a model with examples of extracting beliefs from text.
- Represent the belief state machine in some data structure.
- Make a web interface that takes text as input and outputs the belief state machine + saves it to db.

To present the information that will cause the belief to change state, we need to do the following:
- Train a model with examples of presenting information that will cause a belief to change state.
- Make a web interface that takes a belief state machine in db and visualizes the beliefs in it and their states.
- Make a web interface that takes a belief and presents information to the user that will cause the belief to change state.

---

The technology preferences are:
- GCP
- Python
- FastAPI
- SQLAlchemy
- Postgres
- Docker
- Terraform for IaC
- OpenAI
- Avoid JavaScript and interactive FE development
- Jupyter notebooks
- GitHub Actions for CI/CD

---

Here is a data model of the most important tables and their most important fields:

Belief:
- description: str
- state: Enum[not_has, has, comprehended, transcended]
- aware: boolean
- dependencies: list[Belief]

BeliefStateMachine:
- beliefs: list[Belief]

StateTransition:
- before_belief: Belief
- after_belief: Belief

Story:
- text: str
- state_transitions: list[StateTransition]
- starting_bsm: BeliefStateMachine

---

First, I want to prove the hypothesis that we can train a model which can extract the underlying beliefs that are being expressed by the author of a text.

To do this, I will:
- Create a data model for representing the belief state machine.
- Make examples data with help from LLMs.
- Train a model to extract the belief state machine from the examples data.

What is a good approach to take to prove the hypothesis?
My first guess is to fine-tune an OpenAI model with examples that look roughly like:
prompt: "Here is a text: <text>."
response: "The beliefs in this text are <beliefs>."

Is this a good approach or is there something better I should be doing?

---

Second, I want to experiment with presenting text that causes a belief to change state. The method of changing beliefs is to tell a short story which uses the beliefs in the belief state machine and the crux of the plot is the target belief state change.

What is a good approach to take to experiement here?
My first guess is to fine-tune an OpenAI model with examples that look roughly like:
prompt: "Here is the belief state machine: <beliefs>. Here is the target belief state change: <belief state change>. Tell a short story that causes the target belief state change."
response: "<story>."

Is this a good approach or is there something better I should be doing?

---

Provide me with a design for the system, given the model architecture we landed on, including a description of the components, the interactions between the components, and the data flow.

Provide me with a list of the pros and cons of the design.

---

Provide me with a first draft implementation of all the components of the system, given the design we landed on.
As a first step, let's make the system work locally.

---

Now let's make the system work in the cloud.
