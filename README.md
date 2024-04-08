# moto-fastapi-webapp

Simple proof-of-concept minimal web application for browsing S3 buckets using FastAPI for dynamic
routing and Moto for mocking AWS services for tests and development.

# Running w/ moto

1. Clone the repository. Ensure you have Python >= 3.11 and Poetry installed.

2. Install the project with Poetry:

```bash
poetry install
```

3. Run the application with uvicorn.

```bash
poetry run uvicorn src.app:app --reload
```

And open the application in your browser at `http://localhost:8000`.

# Acknowledgements

Author(s):

- David Sillman <dsillman2000@gmail.com>