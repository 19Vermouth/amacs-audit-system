from crewai import Agent


def create_agents():



    data_ingestor = Agent(
        role="Data Ingestor",
        goal="Convert raw financial data into a clean, structured format for analysis",
        backstory=(
            "Expert in ETL pipelines and financial preprocessing."
        ),
        verbose=True,
        allow_delegation=False
    )

    fraud_detector = Agent(
        role="Fraud Detection Analyst",
        goal="Identify suspicious transactions using anomaly detection",
        backstory=(
            "Expert in fraud detection using statistical techniques."
        ),

        verbose=True,
        allow_delegation=False
    )

    compliance_checker = Agent(
        role="Compliance Officer",
        goal="Ensure transactions comply with regulations",
        backstory=(
            "Expert in financial compliance and audit standards."
        ),

        verbose=True,
        allow_delegation=False
    )

    report_generator = Agent(
        role="Audit Report Generator",
        goal="Generate structured audit report",
        backstory=(
            "Expert in financial reporting and audit summaries."
        ),

        verbose=True,
        allow_delegation=False
    )

    return {
        "ingestor": data_ingestor,
        "fraud_detector": fraud_detector,
        "compliance_checker": compliance_checker,
        "report_generator": report_generator
    }