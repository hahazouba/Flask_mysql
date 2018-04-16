# -*- coding:utf-8 -*-


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate,MigrateCommand
from flask_script import Shell,Manager

app = Flask(__name__)
manager = Manager(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:mysql@127.0.0.1'

@app.route('/')
def index():
    return 'index'

if __name__ == '__main__':
    app.run()