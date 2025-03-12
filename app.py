from flask import Flask, request, render_template, redirect, url_for, flash
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

app = Flask(__name__)
app.secret_key = "your_secret_key"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Home Route
@app.route("/")
def home():
    return render_template("index.html")

# Upload Route
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        flash("No file selected.")
        return redirect(url_for("home"))
    file = request.files["file"]
    if file.filename == "":
        flash("No file selected.")
        return redirect(url_for("home"))
    if file and file.filename.endswith(".csv"):
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)
        flash("File uploaded successfully.")
        return redirect(url_for("analyze", filename=file.filename))
    else:
        flash("Invalid file format. Please upload a CSV file.")
        return redirect(url_for("home"))

# Analyze Route
@app.route("/analyze/<filename>")
def analyze(filename):
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    try:
        df = pd.read_csv(file_path)
        summary = df.describe().to_html()
        return render_template("analyze.html", filename=filename, summary=summary, columns=df.columns.tolist())
    except Exception as e:
        flash(f"Error processing file: {e}")
        return redirect(url_for("home"))

# Visualization Route
@app.route("/visualize", methods=["POST"])
def visualize():
    column_x = request.form.get("column_x")
    column_y = request.form.get("column_y")
    chart_type = request.form.get("chart_type")
    filename = request.form.get("filename")
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    try:
        df = pd.read_csv(file_path)
        plt.figure(figsize=(10, 6))
        if chart_type == "scatter":
            sns.scatterplot(data=df, x=column_x, y=column_y)
        elif chart_type == "bar":
            sns.barplot(data=df, x=column_x, y=column_y)
        elif chart_type == "hist":
            sns.histplot(data=df[column_x], bins=30, kde=True)
        else:
            flash("Invalid chart type selected.")
            return redirect(url_for("analyze", filename=filename))
        chart_path = os.path.join("static", "chart.png")
        plt.savefig(chart_path)
        plt.close()
        return render_template("visualize.html", chart_path=chart_path, filename=filename)
    except Exception as e:
        flash(f"Error generating visualization: {e}")
        return redirect(url_for("analyze", filename=filename))

if __name__ == "__main__":
    app.run(debug=True)
