from fluxion.workflows.abstract_workflow import AbstractWorkflow
from fluxion.core.agents.agent import Agent
from fluxion.workflows.agent_node import AgentNode
from fluxion.models.message_model import Message, MessageHistory
import json


# Step 1: Define Mock Agents for Demonstration
class DataPreprocessingAgent(Agent):
    def execute(self, messages: MessageHistory):
        # Simulate preprocessing data
        processed_data = messages[-1].content.strip().lower()
        return {
            "messages": MessageHistory(messages=[Message(role="system", content=processed_data)])
        }


class DataAnalysisAgent(Agent):
    def execute(self, messages: MessageHistory):
        # Simulate analyzing processed data
        analysis_result = {"word_count": len(messages[-1].content.split())}
        return {
            "messages": MessageHistory(messages=[Message(role="system", content=json.dumps(analysis_result))])
        }

class ReportGenerationAgent(Agent):
    def execute(self, messages: MessageHistory):
        # Simulate generating a report
        analysis_result = json.loads(messages[-1].content)
        report = f"Report: Word count is {analysis_result['word_count']}."
        return {
            "messages": MessageHistory(messages=[Message(role="system", content=report)])
        }



class DataProcessingWorkflow(AbstractWorkflow):
    def __init__(self):
        super().__init__(name="DataProcessingWorkflow")

    def define_workflow(self):
        # Create nodes
        preprocessing_node = AgentNode(
            name="DataPreprocessing",
            agent=DataPreprocessingAgent("PreprocessingAgent"),
            outputs=["messages"]
        )
        analysis_node = AgentNode(
            name="DataAnalysis",
            agent=DataAnalysisAgent("AnalysisAgent"),
            dependencies=[preprocessing_node],
            inputs={"messages": "DataPreprocessing.messages"},
            outputs=["messages"]
        )
        report_node = AgentNode(
            name="ReportGeneration",
            agent=ReportGenerationAgent("ReportAgent"),
            dependencies=[analysis_node],
            inputs={"messages": "DataAnalysis.messages"},
            outputs=["messages"]
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
    inputs = {
        "messages": MessageHistory(messages=[Message(role="user", content="Hello, World!")])
    }
    
    # Create and execute the workflow
    workflow = DataProcessingWorkflow()
    workflow.define_workflow()
    results = workflow.execute(inputs = inputs)
    
    # Print the results
    for node_name, result in results.items():
        print(f"Results from {node_name}: {result}")
