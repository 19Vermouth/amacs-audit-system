from crewai import Task

def create_tasks(agents, data):

    ingest_task = Task(
        description=f"""
        Analyze and clean the following dataset:
        {data}

        Ensure:
        - Remove duplicates
        - Standardize date and amount formats
        - Handle missing values
        """,
        expected_output="Cleaned and structured transaction dataset with standardized fields",
        agent=agents["ingestor"]
    )

    compliance_task = Task(
        description="""
        Check the dataset for compliance violations.

        Rules to check:
        - High-value transactions (> threshold)
        - Transactions at unusual hours (night)
        - Missing or inconsistent fields
        """,
        expected_output="List of compliance violations with transaction IDs and reasons",
        agent=agents["compliance_checker"]
    )

    fraud_task = Task(
        description="""
        Detect anomalies and suspicious patterns in the dataset.

        Use:
        - Statistical anomalies
        - Unusual transaction frequency
        - Suspicious amount distributions
        """,
        expected_output="List of suspicious transactions with anomaly explanations and risk scores",
        agent=agents["fraud_detector"]
    )

    report_task = Task(
        description="""
        Generate a final audit report combining all findings.

        Include:
        - Summary of dataset
        - Compliance issues
        - Fraud detection results
        - Risk assessment
        """,
        expected_output="Structured audit report with summary, fraud flags, compliance issues, and overall risk score",
        agent=agents["report_generator"]
    )

    return [ingest_task, compliance_task, fraud_task, report_task]