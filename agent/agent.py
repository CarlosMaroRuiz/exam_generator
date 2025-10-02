from pydantic_ai import Agent
from dotenv import load_dotenv
from .schema import Test
from .system_promp import SYSTEM_PROMPT
load_dotenv()

agent = Agent(
    "deepseek:deepseek-chat",
    output_type=Test,
    system_prompt=SYSTEM_PROMPT
)

async def execute_agent(input:str):
    try:
        result = await agent.run(input)
        return result.output.result
    except Exception:
        return "hubo un error al generar el examen"