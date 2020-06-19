from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__) #create an instance

@app.route('/optionpricing', methods=['POST', 'GET'])
def taolao():
    if request.method == 'POST':
        para = float(request.form('content')) +
        redirect('/optionpricing')
    else:
        return(render_template('optionpricing.html', tasks = 'the input is', task))


if __name__ == "__main__":
    app.run(debug=True)
