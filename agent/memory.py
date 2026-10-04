from __future__ import annotations
from typing import Dict, List, Any

class AgentMemory:
    def __init__(self) -> None:
        self.working_memory: Dict[str, Any] = {}
        self.step_history: List[Dict[str, Any]] = []
        self.facts: Dict[str, Any] = {}

    def add_step_result(self, step: Any, result: Any, observations: str) -> None:
        self.step_history.append({
            "step_number": getattr(step, 'step_number', None) if hasattr(step, 'step_number') else step,
            "result_success": getattr(result, 'success', None) if hasattr(result, 'success') else result,
            "observations": observations
        })

    def get_context_summary(self) -> str:
        summary = "Known Facts:\n"
        for k, v in self.facts.items():
            summary += f"- {k}: {v}\n"
        summary += "\nRecent Steps:\n"
        for step in self.step_history[-5:]:
            success_str = "Success" if step.get('result_success') else "Failed"
            summary += f"- Step {step.get('step_number')}: {success_str} - {step.get('observations')}\n"
        return summary

    def get_relevant_info(self, query: str) -> str:
        query_words = set(query.lower().split())
        relevant_facts = {}
        for k, v in self.facts.items():
            fact_words = set(str(k).lower().split() + str(v).lower().split())
            if query_words.intersection(fact_words):
                relevant_facts[k] = v
        
        if not relevant_facts:
            return "No relevant info found."
        
        res = "Relevant info:\n"
        for k, v in relevant_facts.items():
            res += f"- {k}: {v}\n"
        return res

    def store_fact(self, key: str, value: Any) -> None:
        self.facts[key] = value

    def get_facts(self) -> Dict[str, Any]:
        return self.facts

    def clear(self) -> None:
        self.working_memory.clear()
        self.step_history.clear()
        self.facts.clear()
