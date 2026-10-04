from __future__ import annotations
import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI

class LLMClient:
    def __init__(self, model: str = 'gpt-4o-mini', api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=self.api_key)
        self._total_tokens_used = 0
        self._estimated_cost = 0.0
        
        self.cost_map = {
            'gpt-4o-mini': (0.00015, 0.0006),
            'gpt-4o': (0.005, 0.015)
        }

    @property
    def total_tokens_used(self) -> int:
        return self._total_tokens_used

    @property
    def estimated_cost(self) -> float:
        return self._estimated_cost

    def _update_usage(self, usage: Any) -> None:
        if usage:
            self._total_tokens_used += usage.total_tokens
            cost_rates = self.cost_map.get(self.model, (0.0, 0.0))
            self._estimated_cost += (usage.prompt_tokens / 1000.0) * cost_rates[0]
            self._estimated_cost += (usage.completion_tokens / 1000.0) * cost_rates[1]

    async def _with_retry(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        max_retries = 3
        base_delay = 1.0
        for attempt in range(max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                await asyncio.sleep(base_delay * (2 ** attempt))

    async def chat(self, messages: List[Dict[str, str]], temperature: float = 0.2, response_format: Optional[Dict[str, Any]] = None) -> str:
        async def _call() -> str:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
            }
            if response_format:
                kwargs["response_format"] = response_format
            
            response = await self.client.chat.completions.create(**kwargs)
            self._update_usage(response.usage)
            return response.choices[0].message.content or ""
            
        return await self._with_retry(_call)

    async def chat_json(self, messages: List[Dict[str, str]], temperature: float = 0.1) -> dict:
        async def _call() -> dict:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                response_format={"type": "json_object"}
            )
            self._update_usage(response.usage)
            content = response.choices[0].message.content or "{}"
            return json.loads(content)
            
        return await self._with_retry(_call)

    async def function_call(self, messages: List[Dict[str, str]], functions: List[Dict[str, Any]], temperature: float = 0.1) -> dict:
        async def _call() -> dict:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                tools=[{"type": "function", "function": f} for f in functions],
                tool_choice="auto"
            )
            self._update_usage(response.usage)
            msg = response.choices[0].message
            if msg.tool_calls:
                call = msg.tool_calls[0].function
                return {
                    "name": call.name,
                    "arguments": json.loads(call.arguments)
                }
            return {"name": None, "arguments": {}}
            
        return await self._with_retry(_call)
