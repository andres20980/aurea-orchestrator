"""Simulation orchestrator for running mock agents and models."""

import time
from typing import Any, Dict, List, Optional
from aurea.simulation.mock_agent import MockAgent
from aurea.simulation.mock_model import MockModel


class SimulationOrchestrator:
    """Orchestrator for simulation mode."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize simulation orchestrator.
        
        Args:
            config: Configuration dictionary from YAML file
        """
        self.config = config
        self.agents = {}
        self.models = {}
        self.metrics = []
        self._initialize_components()

    def _initialize_components(self):
        """Initialize mock agents and models from config."""
        # Initialize agents
        agents_config = self.config.get("agents", [])
        for agent_config in agents_config:
            name = agent_config.get("name")
            if name:
                self.agents[name] = MockAgent(name, agent_config)

        # Initialize models
        models_config = self.config.get("models", [])
        for model_config in models_config:
            name = model_config.get("name")
            if name:
                self.models[name] = MockModel(name, model_config)

    def run_simulation(self, scenarios: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Run simulation scenarios.
        
        Args:
            scenarios: List of scenario dictionaries. If None, uses config scenarios.
            
        Returns:
            Simulation results
        """
        if scenarios is None:
            scenarios = self.config.get("scenarios", [])

        start_time = time.time()
        results = []

        for i, scenario in enumerate(scenarios):
            scenario_result = self._run_scenario(scenario, i)
            results.append(scenario_result)
            self.metrics.append(scenario_result)

        end_time = time.time()

        summary = {
            "total_scenarios": len(scenarios),
            "total_time": end_time - start_time,
            "results": results,
            "agents_used": list(self.agents.keys()),
            "models_used": list(self.models.keys()),
        }

        return summary

    def _run_scenario(self, scenario: Dict[str, Any], scenario_index: int) -> Dict[str, Any]:
        """Run a single scenario.
        
        Args:
            scenario: Scenario configuration
            scenario_index: Index of the scenario
            
        Returns:
            Scenario results
        """
        scenario_start = time.time()
        
        scenario_result = {
            "scenario_id": scenario.get("id", f"scenario_{scenario_index}"),
            "name": scenario.get("name", f"Scenario {scenario_index}"),
            "timestamp": scenario_start,
            "agent_results": [],
            "model_results": [],
        }

        # Execute agent tasks
        agent_tasks = scenario.get("agent_tasks", [])
        for task in agent_tasks:
            agent_name = task.get("agent")
            if agent_name in self.agents:
                agent = self.agents[agent_name]
                result = agent.execute(task)
                scenario_result["agent_results"].append(result)

        # Execute model predictions
        model_tasks = scenario.get("model_tasks", [])
        for task in model_tasks:
            model_name = task.get("model")
            if model_name in self.models:
                model = self.models[model_name]
                result = model.predict(task.get("input", {}))
                scenario_result["model_results"].append(result)

        scenario_end = time.time()
        scenario_result["duration"] = scenario_end - scenario_start
        scenario_result["status"] = "completed"

        return scenario_result

    def get_metrics(self) -> List[Dict[str, Any]]:
        """Get collected metrics.
        
        Returns:
            List of metrics
        """
        return self.metrics

    def get_summary_statistics(self) -> Dict[str, Any]:
        """Get summary statistics from metrics.
        
        Returns:
            Summary statistics
        """
        if not self.metrics:
            return {"error": "No metrics collected"}

        total_scenarios = len(self.metrics)
        total_agent_executions = sum(
            len(m.get("agent_results", [])) for m in self.metrics
        )
        total_model_predictions = sum(
            len(m.get("model_results", [])) for m in self.metrics
        )

        agent_success_count = sum(
            1 for m in self.metrics
            for r in m.get("agent_results", [])
            if r.get("status") == "success"
        )

        return {
            "total_scenarios": total_scenarios,
            "total_agent_executions": total_agent_executions,
            "total_model_predictions": total_model_predictions,
            "agent_success_rate": agent_success_count / total_agent_executions if total_agent_executions > 0 else 0,
            "agents": {name: agent.get_capabilities() for name, agent in self.agents.items()},
            "models": {name: model.get_metadata() for name, model in self.models.items()},
        }
