import yaml
from pathlib import Path
from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv

from pydantic import BaseModel, Field

load_dotenv()

# Use Path for file locations
current_dir = Path(__file__).parent
agents_config_path = current_dir / "config" / "agents.yaml"
tasks_config_path = current_dir / "config" / "tasks.yaml"

# Load YAML configuration files
with open(agents_config_path, "r") as file:
    agents_config = yaml.safe_load(file)

with open(tasks_config_path, "r") as file:
    tasks_config = yaml.safe_load(file)

class BeliefLayer(BaseModel):
    beliefs: list[str] = Field(..., description="List of beliefs")

# Example text (you can replace this with any text input)
default_text = """
I thought China was bad. I think China is bad. I’m here and things don’t seem so bad, so something’s up. I began to think about why I think about China so negatively. All the Chinese people I’ve known in Canada have been so wonderful and Chinese culture is so unoffensive. I realized that all the negative things I think about China comes from Western media and its regurgitation.

I tried to think of two pieces of news that implied China is ‘bad’. Something that portrayed/referenced it as doing bad things or being a bad place. It was easy - I came up with 5+ instantly.

Then I tried to think of two pieces of news that implied China is ‘good’. Something that portrayed it as doing good things or being a good place. I had a hard time coming up with any.

Are things that are good for the world never associated with China? Do good things that may be interesting to Western audiences never happen in China? After thinking hard, I came up with pieces like,

“China’s economy is doing really well.”

“Chinese have a burgeoning middle class.”

“China is building the largest < something > in the world.”

The thing is, I don’t feel good about China when I read these things. I think (or feel like I’m supposed to think),

“Uh, oh. They’re going to beat us.”

or

“Haha, China is such a weird, backwards place.”

and that’s because articles are written with that perspective. When Western articles reference China, it is either with fear or condescension. It’s especially prevalent in technology-related articles.

Does China deserve this treatment from Western media? Maybe, maybe not. The condescension is certainly unhealthy for both sides. What makes me uncomfortable is that there’s a prevailing, unchallengeable attitude towards China and I’ve been unknowingly conditioned to heed it.
"""

default_context = """
The author's name is Douglas.
The author is a 25-year-old Canadian who studied software engineering at the university of waterloo.
They grew up in rural Ottawa, Ontario. They have Irish, British, and Danish ancestry. They were raised upper-middle class with parents who were both engineers.
They travelled quite alot as a child and adult.
"""

@CrewBase
class ExtractBeliefsWriteParableCrew:
    agents_config: str = 'config/agents.yaml'
    tasks_config: str = 'config/tasks.yaml'

    def __init__(self, text: str, context: str):
        self.text = text if text else default_text
        self.context = context if context else default_context

    @agent
    def extractor(self):
        return Agent(
            config=self.agents_config["extractor"],
            allow_delegation=False,
            verbose=True
        )

    @agent
    def modeller(self):
        return Agent(
            config=self.agents_config["modeller"],
            allow_delegation=False,
            verbose=True
        )
    
    @task
    def first_order_beliefs_task(self):
        return Task(
            description=self.tasks_config["first_order_beliefs"]["description"].format(text=self.text, context=self.context),
            expected_output=self.tasks_config["first_order_beliefs"]["expected_output"],
            output_json=BeliefLayer,
            agent=self.extractor()
        )

    @task
    def next_order_beliefs_task_1(self):
        return Task(
            description=self.tasks_config["next_order_beliefs"]["description"].format(text=self.text, context=self.context),
            context=[self.first_order_beliefs_task()],
            expected_output=self.tasks_config["next_order_beliefs"]["expected_output"],
            output_json=BeliefLayer,
            agent=self.extractor()
        )

    @task
    def next_order_beliefs_task_2(self):
        return Task(
            description=self.tasks_config["next_order_beliefs"]["description"].format(text=self.text, context=self.context),
            context=[self.first_order_beliefs_task(), self.next_order_beliefs_task_1()],
            expected_output=self.tasks_config["next_order_beliefs"]["expected_output"],
            output_json=BeliefLayer,
            agent=self.extractor(),
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.extractor(), self.modeller()],
            tasks=[
                self.first_order_beliefs_task(),
                self.next_order_beliefs_task_1(),
                self.next_order_beliefs_task_2()
            ],
            verbose=True,
            process=Process.sequential
        )


@CrewBase
class WriteParableCrew:
    agents_config: str = 'config/agents.yaml'
    tasks_config: str = 'config/tasks.yaml'

    def __init__(self, belief: str, action: str, text: str, context: str):
        self.belief = belief
        self.action = action
        self.text = text if text else default_text
        self.context = context if context else default_context
    
    @agent
    def writer(self):
        return Agent(
            config=self.agents_config["writer"],
            allow_delegation=False,
            verbose=True
        )

    @task
    def write_parable_task(self):
        return Task(
            description=self.tasks_config["write_parable"]["description"].format(text=self.text, context=self.context, belief=self.belief, action=self.action),
            expected_output=self.tasks_config["write_parable"]["expected_output"],
            agent=self.writer()
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.writer()],
            tasks=[self.write_parable_task()],
            verbose=True,
            process=Process.sequential
        )
