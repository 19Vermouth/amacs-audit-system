from crewai import Crew
from dotenv import load_dotenv
from crew.agents import create_agents
from crew.tasks import create_tasks

def run_crew(data):

    load_dotenv()
    agents = create_agents()
    tasks = create_tasks(agents, data)

    crew = Crew(
        agents=list(agents.values()),
        tasks=tasks,
        verbose=True,
    )

    result = crew.kickoff()
    return result
