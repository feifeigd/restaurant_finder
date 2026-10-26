
import logging
import os

import click
from dotenv import load_dotenv

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from agent import RestaurantAgent
from agent_executor import RestaurantAgentExecutor

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

class MissingAPIKeyError(Exception):
    """Exception for missing API key."""

@click.command()
@click.option("--host", default="localhost")
@click.option("--port", default=10003)
def main(host, port):
    try:
        if not os.getenv("GOOGLE_GENAI_USE_VERTEXAI") == "TRUE":
            if not os.getenv("GEMINI_API_KEY"):
                raise MissingAPIKeyError(
                    "GEMINI_API_KEY environment variable not set and"
                    " GOOGLE_GENAI_USE_VERTEXAI is not TRUE."
                )

        base_url = f"http://{host}:{port}"
        agent = RestaurantAgent(base_url=base_url)
        agent_executor = RestaurantAgentExecutor(agent)
        request_handler = DefaultRequestHandler(
            agent_executor=agent_executor,
            task_store=InMemoryTaskStore(),
        )

        app = A2AStarletteApplication(
            agent_card=agent.agent_card,
            http_handler=request_handler,
        ).build()
        app.add_middleware(
            CORSMiddleware,
            allow_origin_regex=r"http://localhost:\d+",
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        app.mount("/static", StaticFiles(directory="images"))

        import uvicorn
        uvicorn.run(app, host=host, port=port)

    except MissingAPIKeyError as e:
        logger.error(f"Error: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"An error occured during server startup: {e}")
        exit(1)

if "__main__" == __name__:
    main()
