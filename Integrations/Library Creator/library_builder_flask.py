import logging
from flask import Flask, request, render_template, redirect, url_for, flash
from library_builder import library_creation

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = Flask(__name__)
app.secret_key = "your_secret_key"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    try:
        library = request.form["library"]
        riskpattern = request.form["riskpattern"]
        usecase = request.form["usecase"]
        threat = request.form["threat"]
        threat_desc = request.form["threat_desc"]
        weakness = request.form["weakness"]
        countermeasure = request.form["countermeasure"]
        countermeasure_desc = request.form["countermeasure_desc"]
        standardref = request.form["standardref"]
        standardname = request.form["standardname"]
        suppstandref = request.form["suppstandref"]

        library_creation(
            library,
            riskpattern,
            usecase,
            threat,
            threat_desc,
            weakness,
            countermeasure,
            countermeasure_desc,
            standardref,
            standardname,
            suppstandref,
        )
        flash("Library creation process completed successfully.", "success")
    except Exception as e:
        logging.error(f"Error during library creation: {e}")
        flash(f"An error occurred: {e}", "danger")

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
