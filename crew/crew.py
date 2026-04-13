from crewai import Crew
from crew.agents import create_agents
from crew.tasks import create_tasks

def run_crew(data):

    agents = create_agents()
    tasks = create_tasks(agents, data)

    crew = Crew(
        agents=list(agents.values()),
        tasks=tasks,
        verbose=True
    )

    result = crew.kickoff()
    return result
