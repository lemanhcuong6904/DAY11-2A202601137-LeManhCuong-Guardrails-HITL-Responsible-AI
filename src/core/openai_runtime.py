"""
Minimal OpenAI-backed runtime used by this lab.

It preserves the small agent/runner/plugin surface the lab needs, without
depending on a vendor agent SDK. Plugins can block user input before the model call and
can rewrite/block model output after the OpenAI response is produced.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from types import SimpleNamespace
from uuid import uuid4

from core.config import MODEL_NAME


@dataclass
class Part:
    text: str

    @classmethod
    def from_text(cls, text: str) -> "Part":
        return cls(text=text)


@dataclass
class Content:
    role: str
    parts: list[Part] = field(default_factory=list)


types = SimpleNamespace(Content=Content, Part=Part)


class BasePlugin:
    """Small plugin base compatible with the callbacks used in the lab."""

    def __init__(self, name: str):
        self.name = name


@dataclass
class InvocationContext:
    user_id: str = "student"
    session_id: str | None = None


@dataclass
class LlmAgent:
    model: str
    name: str
    instruction: str


@dataclass
class Session:
    id: str
    user_id: str
    messages: list[dict[str, str]] = field(default_factory=list)


class InMemorySessionService:
    def __init__(self):
        self._sessions: dict[tuple[str, str, str], Session] = {}

    async def create_session(self, *, app_name: str, user_id: str) -> Session:
        session = Session(id=str(uuid4()), user_id=user_id)
        self._sessions[(app_name, user_id, session.id)] = session
        return session

    async def get_session(self, *, app_name: str, user_id: str, session_id: str) -> Session:
        return self._sessions[(app_name, user_id, session_id)]


@dataclass
class LlmResponse:
    content: Content


@dataclass
class Event:
    content: Content


class InMemoryRunner:
    def __init__(self, *, agent: LlmAgent, app_name: str, plugins: list | None = None):
        self.agent = agent
        self.app_name = app_name
        self.plugins = plugins or []
        self.session_service = InMemorySessionService()

    async def run_async(self, *, user_id: str, session_id: str, new_message: Content):
        context = InvocationContext(user_id=user_id, session_id=session_id)

        for plugin in self.plugins:
            callback = getattr(plugin, "on_user_message_callback", None)
            if callback is None:
                continue
            blocked = await callback(
                invocation_context=context,
                user_message=new_message,
            )
            if blocked is not None:
                yield Event(content=blocked)
                return

        prompt = _content_text(new_message)
        response_text = await _call_openai(
            model=self.agent.model or MODEL_NAME,
            instructions=self.agent.instruction,
            prompt=prompt,
        )
        llm_response = LlmResponse(
            content=Content(role="model", parts=[Part.from_text(response_text)])
        )

        for plugin in self.plugins:
            callback = getattr(plugin, "after_model_callback", None)
            if callback is None:
                continue
            maybe_response = await callback(
                callback_context=context,
                llm_response=llm_response,
            )
            if maybe_response is not None:
                llm_response = maybe_response

        yield Event(content=llm_response.content)


def _content_text(content: Content) -> str:
    if not content or not content.parts:
        return ""
    return "".join(part.text for part in content.parts if getattr(part, "text", None))


async def _call_openai(*, model: str, instructions: str, prompt: str) -> str:
    try:
        from openai import AsyncOpenAI
    except ImportError as exc:
        raise RuntimeError(
            "The OpenAI SDK is not installed. Run `pip install -r requirements.txt`."
        ) from exc

    client = AsyncOpenAI()
    response = await client.responses.create(
        model=model,
        instructions=instructions,
        input=prompt,
    )
    return (getattr(response, "output_text", None) or "").strip()
