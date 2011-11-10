# qi is where you put your notes.
# then they can do things

from flask import Flask, render_template, request, redirect, url_for
from forms import EntryForm, SigninForm, SignupForm
import settings
import logging

app = Flask(__name__)

@app.route("/")
def home():
    """Display the home page"""
    form = EntryForm()
    return render_template("index.html",
                           form=form)

@app.route("/save", methods=['POST'])
def saveentry():
    """Save the entry"""
    return redirect(url_for('home'))
    
@app.route("/signin", methods=['GET', 'POST'])
def signin():
    """Sign the user in"""
    form = SigninForm()
    return render_template("signin.html",
                           form=form)

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    """Register a user"""
    form = SignupForm()
    if request.method == 'POST' and form.validate():
        # Add the user
        print "successful and stuff"
    return render_template("signup.html",
                           form=form)

app.secret_key = settings.APP_SECRET_KEY

if __name__ == '__main__':
    print "Serving on port ", settings.APP_PORT
    app.run(port=settings.APP_PORT, 
            debug=settings.APP_DEBUG_ENABLED, 
            use_reloader=settings.APP_RELOADER_ENABLED)
