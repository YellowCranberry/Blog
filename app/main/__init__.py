from flask import Flask,render_template

# def create_app(): 
app = Flask(__name__) 
#   return app

@app.route('/')
def index():
    return render_template('base.html')

if __name__=='__main__':
    app.run(debug=True)

