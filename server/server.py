from flask import Flask, render_template
import pandas as pd
import logging

app = Flask(__name__)


def run():
    logging.info("Starting flask server!...")
    app.run(debug=True)


@app.route("/")
def main():
    try:
        with open("logfile.log", "r") as f:
            log_lines = [l.strip() for l in f.readlines()[-5:]]
    except FileNotFoundError:
        log_lines = []

    df = pd.read_csv("seen_ads.csv").drop(["id", "zip_code"], axis=1).head(100)

    table_html = df.to_html(
        header="true", index=False, table_id="dataframe", na_rep="/", classes=["stripe"]
    )
    return render_template("table.html", table=table_html, log_lines=log_lines)


if __name__ == "__main__":
    run()
