from flask import Flask

app = Flask(__name__)


@app.route("/")
def main():
    with open("nohup.out", "r") as f:
        lines = f.readlines()

    event_lines = [l for l in lines if "Sleeping" not in l]
    return f"""
        <h2>all updates</h2>
        <textarea rows=20 style='width:100%;'>{''.join(lines)}</textarea>

        <hr>
        <h2>events</h2>
        <textarea rows=20 style='width:100%;'>{''.join(event_lines)}</textarea>
        """
