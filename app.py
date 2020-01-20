from flask import Flask, render_template, make_response

app = Flask(__name__)

@app.route("/")
def index():
    # Todo
    return render_template ("index.html")

@app.route("/login")
def login():
    # Todo
    return render_template ("login.html")

@app.route("/logout")
def logout():
    # Todo
    return

@app.route("/register")
def register():
    # Todo
    return render_template ("register.html")

@app.route("/stl_viewer")
def stl_viewer():
    # Todo
    return render_template ("stl_viewer.html")

@app.route("/basket")
def basket():
    # Todo
    return render_template ("basket.html")

@app.route("/models")
def models():
    # Todo
    return render_template ("models.html")

@app.route("/about")
def about():
    # Todo
    return render_template ("about.html")

if __name__ == "__main__":
    app.run(debug = True)