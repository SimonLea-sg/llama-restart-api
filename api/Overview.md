## Code Structure Design

To separate concerns and ensure maintainability, we will split the application into three files:

config.py: Handles configuration settings using pydantic-settings.
manager.py: Manages the lifecycle of the llama-server subprocess.
main.py: The FastAPI application with endpoints and startup logic.

### Codebase Layout:

project-root/
├── docker/
│   ├── Dockerfile
│   └── .env
├── api/
│   ├── main.py         # FastAPI application
│   ├── config.py       # Pydantic settings
│   └── service.py      # Subprocess logic
└── requirements.txt


