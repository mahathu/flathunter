from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)


@app.route("/")
def main():
    try:
        with open("../nohup.out", "r") as f:
            nohup_lines = [l.strip() for l in f.readlines()[-5:]]
    except FileNotFoundError:
        nohup_lines = []

    df = pd.read_csv("../data/seen_ads.csv").drop(["id", "zip_code"], axis=1).head(100)

    table_html = df.to_html(
        header="true", index=False, table_id="dataframe", na_rep="/", classes=["stripe"]
    )
    return render_template("table.html", table=table_html, nohup_lines=nohup_lines)
