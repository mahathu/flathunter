from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/")
def read_root():
    with open("nohup.out", "r") as f:
        lines = f.readlines()

        event_lines = [l for l in lines if "Sleeping" not in l]

        html_content = f"<h2>last 5 updates</h2>{'<br>'.join(lines[-5:-1])}<hr><h2>last 5 events</h2>{'<br>'.join(event_lines[-5:-1])}"

        return HTMLResponse(content=html_content, status_code=200)
