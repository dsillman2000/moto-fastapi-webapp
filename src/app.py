from fastapi import FastAPI
from fastapi.logger import logger
from fastapi.responses import HTMLResponse
from pathlib import Path

from .s3_utils import S3Context


app = FastAPI()
HTML_J2_DIRECTORY = Path(__file__).parent / "html-j2"


def compile_template(tmpl: str, context: dict = {}) -> str:
    from jinja2 import Environment, FileSystemLoader

    env = Environment(loader=FileSystemLoader(HTML_J2_DIRECTORY))
    template = env.get_template(tmpl)
    return template.render(context)


@app.get("/buckets", response_class=HTMLResponse)
def buckets_page():
    return compile_template(
        "buckets/index.html.j2",
        context=S3Context().dict(),
    )


@app.get("/buckets/{bucket_name}{cwd:path}", response_class=HTMLResponse)
def bucket_browser(bucket_name: str, cwd: str = "/"):
    return compile_template(
        "browser/index.html.j2",
        context=S3Context().dict()
        | {"bucket_name": bucket_name, "cwd": cwd.lstrip("/")},
    )
