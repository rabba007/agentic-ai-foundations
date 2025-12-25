from dataclasses import dataclass
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware,AgentState, HumanInTheLoopMiddleware, wrap_model_call,\
 ModelRequest, ModelResponse, dynamic_prompt
from langchain.chat_models import init_chat_model
from typing_extensions import Callable
from langgraph.types import Command
from langchain.tools import tool, ToolRuntime
from langchain.messages import ToolMessage

load_dotenv(override=True)

@dataclass
class EmailContext:
    email_address: str = "julie@example.com"
    password: str = "abc123"


class AuthenticatedState(AgentState):
    authenticated: bool


@tool
def check_inbox() -> str:
    """Check the inbox for recent emails"""
    return """
    Hi Julie, 
    I'm going to be in town next week and was wondering if we could grab a coffee?
    - best, Jane (jane@example.com)
    """

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an response email"""
    return f"Email sent to {to} with subject {subject} and body {body}"

@tool
def authenticate(email: str, password: str, runtime: ToolRuntime) -> Command:
    """Authenticate the user with the given email and password"""

    if email.strip() == runtime.context.email_address and password.strip() == runtime.context.password :
        return Command(update={
            "authenticated": True,
            "messages":[ToolMessage("Successfully authenticated", tool_call_id = runtime.tool_call_id)]
        })

    else:
        return Command(update={
            "authenticated":False,
            "messages":[ToolMessage("authentication failed", tool_call_id=runtime.tool_call_id)]
        })


@wrap_model_call
async def dynamic_tool_call(
    request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """Allow read inbox and send email tools only if user provides correct email and password"""

    authenticated = request.state.get('authenticated')
    if authenticated:
        tools=[check_inbox, send_email]
    else:
        tools=[authenticate]
    
    request = request.override(tools=tools)

    return await handler(request)


@dynamic_prompt
def dynamic_prompt_for_authorization(request:ModelRequest)->str:
    """Generate system prompt based on authentication status"""

    authenticated_prompt = "You are a helpful assistant that can check the inbox and send emails."
    unauthenticated_prompt = "You are a helpful assistant that can authenticate users."

    authenticated = request.state.get("authenticated")

    if authenticated:
        return authenticated_prompt
    return unauthenticated_prompt

agent = create_agent(
    model=init_chat_model("gpt-4o-mini", model_provider="openai", temperature=.5),
    tools=[authenticate, check_inbox, send_email],
    context_schema=EmailContext,
    state_schema=AuthenticatedState,
    system_prompt="IMPORTANT TOOL RULES:\
  - If you decide to call a tool:\
  - Output ONLY a tool call\
  - Do NOT include any natural language\
  - Do NOT explain the tool call\
  - Do NOT ask follow-up questions\
  - Do NOT include text before or after the tool call",
    middleware=[
        dynamic_prompt_for_authorization,
        dynamic_tool_call,
        HumanInTheLoopMiddleware(
            interrupt_on={
                "send_email":True
            }
        ),
        ModelCallLimitMiddleware(
            thread_limit=10,
            run_limit=5,
            exit_behavior='error'
            )

    ]
)


