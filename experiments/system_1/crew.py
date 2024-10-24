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

@CrewBase
class ExtractBeliefsWriteParableCrew:
    agents_config: str = 'config/agents.yaml'
    tasks_config: str = 'config/tasks.yaml'

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
            description=self.tasks_config["first_order_beliefs"]["description"].format(text=text, context=context),
            expected_output=self.tasks_config["first_order_beliefs"]["expected_output"],
            output_json=BeliefLayer,
            agent=self.extractor()
        )

    @task
    def next_order_beliefs_task_1(self):
        return Task(
            description=self.tasks_config["next_order_beliefs"]["description"].format(text=text, context=context),
            context=[self.first_order_beliefs_task()],
            expected_output=self.tasks_config["next_order_beliefs"]["expected_output"],
            output_json=BeliefLayer,
            agent=self.extractor()
        )

    @task
    def next_order_beliefs_task_2(self):
        return Task(
            description=self.tasks_config["next_order_beliefs"]["description"].format(text=text, context=context),
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

    def __init__(self, text: str, context: str, belief: str):
        self.text = text 
        self.context = context
        self.belief = belief

    
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
            description=self.tasks_config["write_parable"]["description"].format(text=text, context=context, belief=self.belief),
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
