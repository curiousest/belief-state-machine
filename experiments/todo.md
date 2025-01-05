## develop an eval pipeline

https://github.com/openai/evals

### recognition

given a prompt and a looong list of generated text, which ones should be selected?
"in our experience about 5-15% of text is good enough to include"
label the overall text 0-10
pick the text from it to include

### recall 1

given a bunch of different models at different temperatures, generate a lot of text
randomize the order of the text
see which ones are selected by the model
see which ones are labelled by human as good/bad

similarity/distance metric between the model's output to one of the target texts labelled as good

### recall 2

prompt + text => similarity/distance metric to the target text

## debug why the parables suck
1. Try other files/context to see if it's the input
2. Compare against manual text entry to see if it's the api/model
3. Compare different models for parable generation to see if it's the model

make it interactive - pick the belief and what kind of change to generate a parable for
make it "minimum viable belief change" - build a tree of beliefs and operate on the ones that are lowest-level with no overlapping dependencies above them
ex: rome had a strong military and rome's culture incoporated military values => go one level higher 

make it a web app 
- upload/paste files and context
- filter prompt injection

add a bit of memory to the webapp?


## CrewAI open questions

To what degree can/should you manage state across a run with CrewAI?

Here's a contrived example:

Suppose you are building a system that improves essays with ~10 paragraphs.
First, you ask a summarizer agent to summarize each paragraph.
Next, you ask a summarizer agent to summarize each pair of summaries.
Next, you run a text complexity score (non-llm-based) against each paragraph.
Next, you ask a prioritization agent to rank paragraphs + pairs in order of "needs improvement". 
Next, you want to experiment with all the above to see what kinds of outputs the system produces.

What I've found with CrewAI is that it's not clear how to:

Take structured outputs partway through a crew, perform a complex task on it which changes the structure of the data, all the while maintaining a structured global state of all the outputs of agentic/non-agentic tasks that can be used as task inputs or control flow of what agents to run next.

Is that getting too pipeline-y? It seems like crewAI might be more designed for agents fluidly calling one-another, but surely there's a ton of value in a mix of fluid agentic interactions mixed in with pipelines (higher-level control flow).