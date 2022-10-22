from flask import Flask

app = Flask(__name__)

@app.route("/")
def main():
    with open("nohup.out", "r") as f:
        lines = f.readlines()

    event_lines = [l for l in lines if "Sleeping" not in l]
    return f"""
        <h2>last 5 updates</h2>
        <textarea rows=5 style='width:100%;'>{''.join(lines)}</textarea>

        <hr>
        <h2>last 5 events</h2>
        <textarea rows=5 style='width:100%;'>{''.join(event_lines)}</textarea>
        """