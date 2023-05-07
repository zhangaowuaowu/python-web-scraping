from flask import Flask, render_template, request, redirect, url_for
from werkzeug.datastructures import ImmutableDict
import sqlalchemy as db
from flask_moment import Moment
from datetime import datetime
from pathlib import Path
import uuid
import recognition.load_model as model

# query = db.select(table_users.c.username).where(
#     table_users.c.password == '123456')  # 建立指令
# proxy = connection.execute(query)  # 指令execute得到結果proxy
# results = proxy.fetchall()  # 在proxy容器中取出結果
# print(results[2])

#多條資料插入
# user_data = [{'id':1, 'userid':'zhangaowuaowu@gmail.com', 'passwd':'123456', 'userphone':'0975383833'},
#              {'id':2, 'userid':'dawang@gmail.com', 'passwd':'dawang', 'userphone':'0975383833'},
#              {'id':3, 'userid':'abcbca@gmail.com', 'passwd':'abcbca', 'userphone':'0975383833'}]

username = 'root'     # 資料庫帳號
password = '123456'     # 資料庫密碼
host = 'localhost'    # 資料庫位址
port = '3306'         # 資料庫埠號
database = 'userdata'   # 資料庫名稱
table = 'userinfo'   # 表格名稱




app = Flask(__name__)
moment = Moment(app)

# practice start
UPLOAD_FOLDER = Path(__file__).resolve().parent/'static/uploaded'
# practice end

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB


@app.route('/')
def login():
    return render_template('login.html')

@app.route('/check_login', methods=['post'])
def check_login():
    loginmail = request.form['loginmail']
    loginpassword = request.form['loginpassword']

    engine = db.create_engine(f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}', echo=True)
    connection = engine.connect()
    metadata = db.MetaData()
    table_users = db.Table(table, metadata, autoload_with=engine)
    query = db.select(table_users.c.passwd).where(table_users.c.userid==loginmail)
    proxy = connection.execute(query)
    results = proxy.fetchone()
    if results is not None:
        results = list(results)[0]
        if results == loginpassword:
            return redirect(url_for('get_file'))
        else:
            return 'email or password wrong, please try again'
    
    return 'email or password wrong, please try again'


@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/do_register', methods=["post"])
def do_register():
    email = request.form['InputEmail1']
    password1 = request.form['InputPassword1']
    password2 = request.form['InputPassword2']
    phonenumber1 = request.form['InputPhonenumber1']

    if password1 != password2:
        return 'Passwords do not match. Please try again.'
    elif email == '':
        return 'Email address could not blank.'
    elif password1 == '':
        return 'password address could not blank.'
    elif password2 == '':
        return 'password address could not blank.'
    else:
        try:
            # 建立資料庫引擎
            engine = db.create_engine(f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}', echo=True)
            # 建立資料庫連線
            connection = engine.connect()
            # 確定讀取表格
            metadata = db.MetaData()
            table_users = db.Table(
                table, metadata, autoload_with=engine)
            transaction = connection.begin()
            # query = db.select(table_users.c.userid)
            # proxy = connection.execute(query)
            # results = proxy.fetchall()

            # if email not in results:
            query = db.insert(table_users).values(userid=email, passwd=password1 , userphone=phonenumber1)
            proxy = connection.execute(query)
            transaction.commit()
            # else:
            #     return 'email can not be repeated'
        except:
            transaction.rollback()
        finally:
            connection.close()
            engine.dispose()
        return render_template('register_success.html')
        
@app.route('/return_login')
def return_login():
    return redirect(url_for('login'))

@app.route('/rec', methods=['GET', 'POST'])
def get_file():
    if request.method == "GET":
        return render_template('file.html', page_header="upload hand write picture")
    elif request.method == "POST":
        file = request.files['file']
        if file:
            filename = str(uuid.uuid4())+"_"+file.filename
            file.save(app.config['UPLOAD_FOLDER']/filename)
            predict = model.recog_digit(filename)
        return render_template('recog_result.html', page_header="hand writing digit recognition", predict = predict, src = url_for('static', filename=f'uploaded/{filename}'))



if __name__ == '__main__':
    app.run(debug=True)
