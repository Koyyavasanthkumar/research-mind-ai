from backend.graph.workflow import ResearchWorkflow
from backend.models.schemas import ResearchState


def test_workflow_retry_records_failure() -> None:
    workflow = ResearchWorkflow()

    def failing_agent(state: ResearchState) -> ResearchState:
        raise RuntimeError("agent exploded")

    node = workflow._node("Failing Step", "Failing Agent", failing_agent)
    result = ResearchState.model_validate(node(ResearchState(user_query="test").as_graph_dict()))

    assert result.error == "agent exploded"
    assert result.history[-1].attempts == 3
    assert result.history[-1].status == "failed"
