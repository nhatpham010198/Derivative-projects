
import numpy as np
import math
from datetime import datetime
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy



#binding the instance to a very specific Flask application:
app = Flask(__name__) #create an instance
# URI format 'SQLALCHEMY_DATABASE_URI' and 'sqlite:///test.db' go together
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///thisshit.db'

db = SQLAlchemy(app)

# you can declare a model/data base
class NP(db.Model):
    __tablename__ = 'NP'
    id = db.Column(db.Integer, primary_key=True)
    p_0 = db.Column(db.Float)
    n = db.Column(db.Integer)
    v = db.Column(db.Float)
    r = db.Column(db.Float)
    s = db.Column(db.Float)
    country = db.Column(db.String(2))
    T = db.Column(db.Float)
    c = db.Column(db.Float)
    cp = db.Column(db.Integer)
    valuation = db.Column(db.Float)
    round_valuation = db.Column(db.Float)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)


    # id = db.Column(db.Integer, primary_key=True)
    # a_value = db.Column(db.float) #id is a col whose value is integer and unique to every entry (primary key)
    # b_value = db.Column(db.Integer) #content is also a col in the table, non nullable value
    # sumx = db.Column(db.Integer) #created time of a task is a col in the table
    # date_created = db.Column(db.DateTime, default=datetime.utcnow)
    # determine how results are printed out
    def __repr__(self):
        return '<Task %r>' % self.id

db.create_all()
db.session.commit()
# The index function will pass the entries to the show_entries.html template and
# return the rendered one:
#determine what url to where results of the functions are shown.
#route('/') means the url is localhost:5000. route('/home') means the url is localhost:5000/home/

## lattice price
def price(p_0, n, u, d):

    price_lattice = [[0 for _ in range(n+1)] for _ in range(n+1)]
    price_lattice[n][0] = p_0
    for i in range(1,n+1):
        price_lattice[n][i] = price_lattice[n][i-1] * d
    for period in range(1, n + 1):
        for state in range(n, n - period, -1):
            price_lattice[state-1][period] = price_lattice[state][period] * u**2
    return(np.array(price_lattice))

## vanila option
def vanila_option(p_0, n, v, r, s, country, R, T, cp):
    import math
    import numpy as np
    if cp not in [1,-1]:
        raise ValueError('CP should be either 1 (if call) or 0 (if put) ')

    u = math.exp(v*math.sqrt(T/n))
    d = 1/u
    discount = math.exp(r*T/n)
    q = (math.exp((r-R)*T/n)-d)/(u-d)
#     print(u,d,discount,q)
    price_lattice = price(p_0, n, u, d)
    valuation = [[0 for _ in range(n+1)] for _ in range(n+1)]
    portfolio = [[0 for _ in range(n+1)] for _ in range(n+1)]

    if country == 'EU':
        for state in range(n+1):
            valuation[state][n] = max(cp*(price_lattice[state][n] - s), 0)
        for period in range(n-1, -1, -1):
            for state in range(n, n - period - 1, -1):
                valuation[state][period] = ((1-q)*valuation[state][period+1] + q*valuation[state-1][period+1])/discount

                upside_return = valuation[state-1][period+1]
                downside_return = valuation[state][period+1]
                stock = (upside_return-downside_return)/(price_lattice[state-1][period+1]-price_lattice[state][period+1])
                cash  = (upside_return*d-downside_return*u)/(discount*(d-u))
                portfolio[state][period] = (stock,cash)
        return(valuation[n][0], valuation, portfolio)


    elif country == 'US':
        for state in range(n+1):
            valuation[state][n] = max(cp*(price_lattice[state][n] - s), 0)
        for period in range(n-1, -1, -1):
            for state in range(n, n - period - 1, -1):
                valuation[state][period] = max(max(cp*(price_lattice[state][period] - s),0),
                                               ((1-q)*valuation[state][period+1] + q*valuation[state-1][period+1])/discount)

                upside_return = valuation[state-1][period+1]
                downside_return = valuation[state][period+1]
                stock = (upside_return-downside_return)/(price_lattice[state][period]*(u-d))
                cash = (upside_return-downside_return)/(discount*price_lattice[state][period]*(u-d))
                portfolio[state][period] = [stock,cash]

                if valuation[state][period] == max(cp*(price_lattice[state][period] - s),0):
                    exercise = (period,state)

        print('Exercise the US option at period', exercise[0])

        return(valuation[n][0], valuation, portfolio)

    else:
        raise ValueError('country should be either US or EU')

@app.route('/', methods=['POST', 'GET'])
def index():
    #request.method: method of the action
    # request is a class imported above
    if request.method == 'POST':
        #'content' is a section in the website (index.html)
        # option_p_0 = float(request.form['p_0'])
        # option_n = request.form['n']
        # option_v = float(request.form['v'])
        # option_r = float(request.form['r'])
        # option_s = float(request.form['s'])
        # option_country = request.form['country']
        # option_c = request.form['c']
        # option_T = float(request.form['T'])
        # option_cp = float(request.form['cp'])
        # option_p_0 = request.form.get('p_0', type=float)
        # option_n = request.form.get('n', type=int)
        # option_v = request.form.get('v', type=float)
        # option_r = request.form.get('r', type=float)
        # option_s = request.form.get('s', type=float)
        # option_country = request.form.get('country', type='text')
        # option_c = request.form.get('c', type=float)
        # option_T = request.form.get('T', type=float)
        # option_cp = request.form.get('cp', type=int)
        option_p_0 = float(request.form.get('p_0'))
        option_n = int(request.form.get('n'))
        option_v = float(request.form.get('v'))
        option_r = float(request.form.get('r'))
        option_s = float(request.form.get('s'))
        option_country = str(request.form.get('country'))
        option_c = float(request.form.get('c'))
        option_T = float(request.form.get('T'))
        option_cp = int(request.form.get('cp'))
        # option_cp = 1 if typeoption == "Call" else -1



        price = vanila_option(option_p_0, option_n, option_v, option_r, option_s, option_country, option_c, option_T, option_cp)[0]
        # price = sum([option_p_0, option_n, option_v, option_r, option_s, option_c, option_T, option_cp])
        # pass information in the content section (saved as task_content) as new item named new_task
        round_price = round(price, 2)
        new_option = NP(p_0 = option_p_0, n = option_n, v = option_v, r = option_r, s = option_s, country = option_country,
        c = option_c, T = option_T, cp = option_cp, valuation = price, round_valuation = round_price)
        #add new_task to the database (db table)
        # without session and commit, we have to do it mannually (declare new entries
        # and type these commands to add new entries to the table)
        try:
            db.session.add(new_option)
            db.session.commit()
            return redirect('/')

        except:
            return 'There was an issue adding your task'

    #if GET, return all item in the table
    else:
        options = NP.query.order_by(NP.date_created).all()
        # price = vanila_option(option_p_0, option_n, option_v, option_r, option_s, option_country, option_c, option_T, option_cp)
        # new_option = NP(p_0 = 100, n = 15, v = 0.3, r = 0.02, s = 110, country = 'US', c = 0.01, T = 0.25, cp = 1, valuation = 112)
        return (render_template('machine.html', options = options)) #render a template, and show all value assigned to 'tasks' variable


if __name__ == "__main__":
    app.run(debug=True)
