from fluxion.workflows.abstract_workflow import AbstractWorkflow
from fluxion.core.agents.agent import Agent
from fluxion.workflows.agent_node import AgentNode


# Step 1: Define Mock Agents for Demonstration
class DataPreprocessingAgent(Agent):
    def execute(self, raw_data):
        # Simulate preprocessing data
        processed_data = raw_data.strip().lower()
        return {"processed_data": processed_data}


class DataAnalysisAgent(Agent):
    def execute(self, processed_data):
        # Simulate analyzing processed data
        analysis_result = {"word_count": len(processed_data.split())}
        return {"analysis_result": analysis_result}


class ReportGenerationAgent(Agent):
    def execute(self, analysis_result):
        # Simulate generating a report
        report = f"Report: Word count is {analysis_result['word_count']}."
        return {"report": report}



class DataProcessingWorkflow(AbstractWorkflow):
    def __init__(self):
        super().__init__(name="DataProcessingWorkflow")

    def define_workflow(self):
        # Create nodes
        preprocessing_node = AgentNode(
            name="DataPreprocessing",
            agent=DataPreprocessingAgent("PreprocessingAgent")
        )
        analysis_node = AgentNode(
            name="DataAnalysis",
            agent=DataAnalysisAgent("AnalysisAgent"),
            dependencies=[preprocessing_node]
        )
        report_node = AgentNode(
            name="ReportGeneration",
            agent=ReportGenerationAgent("ReportAgent"),
            dependencies=[analysis_node]
        )
        
        # Add nodes to the workflow
        self.add_node(preprocessing_node)
        self.add_node(analysis_node)
        self.add_node(report_node)

    def execute(self, inputs):
        # Start the workflow execution
        return super().execute(inputs)


if __name__ == "__main__":
    # Inputs for the workflow
    inputs = {"raw_data": "  Hello World! Welcome to the workflow demo.  "}
    
    # Create and execute the workflow
    workflow = DataProcessingWorkflow()
    results = workflow.execute(inputs)
    
    # Print the results
    for node_name, result in results.items():
        print(f"Results from {node_name}: {result}")
