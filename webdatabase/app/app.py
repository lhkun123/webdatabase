import traceback
from flask import *
from flask_wtf import FlaskForm
from wtforms import Form, validators, widgets, PasswordField, SubmitField, BooleanField
from wtforms.fields import simple, html5
import pymysql
from wtforms.validators import DataRequired, EqualTo, Length,Email
from werkzeug.security import generate_password_hash, check_password_hash
import tkinter
import tkinter.messagebox
import asyncio
import base64
from datetime import timedelta
import math
import plotly.offline
from plotly.graph_objs import Scatter,Layout,Data
import plotly.graph_objs as go

app = Flask(__name__)
app.send_file_max_age_default = timedelta(seconds=1)
app.secret_key = 'TPmi4aLWRbyVq8zu9v82dWYW1'

class RegisterForm(Form):
    username = simple.StringField(
        #label='注册用户：',
        validators=[
            validators.DataRequired(message='Username cannot be empty'),
            validators.Length(min=6, max=18, message='用户名长度必须大于%(min)d且小于%(max)d')
        ],
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control',
                   "placeholder":"please enter username"}
    )
    email=simple.PasswordField(
        validators=[DataRequired(),Email(),Length(1,254)],
    widget = widgets.TextInput(),
    render_kw = {'class': 'form-control',
                          "placeholder": "please enter your email"}
    )
    password = simple.PasswordField(
        validators=[
            validators.DataRequired(message='密码不能为空'),
            validators.Length(min=6, message='用户名长度必须大于%(min)d'),
            validators.Regexp(regex="[0-9a-zA-Z]{6,}",message='密码不允许使用特殊字符')
        ],
        widget=widgets.PasswordInput(),
        render_kw={'class': 'form-control',
                   "placeholder":"please enter password"}
    )
    RepeatPassword = simple.PasswordField(
        #label='重复密码：',
        validators=[
            validators.DataRequired(message='密码不能为空'),
            validators.Length(min=6, message='密码长度必须大于%(min)d'),
            validators.Regexp(regex="[0-9a-zA-Z]{6,}",message='密码不允许使用特殊字符'),
            validators.EqualTo("password",message="两次密码输入必须一致")
        ],
        widget=widgets.PasswordInput(),
        render_kw={'class': 'form-control',
                   "placeholder":"please enter password again"}
    )
    submit = simple.SubmitField(
        label="register",
        render_kw={ "class":"btn btn-success" }
    )
class LoginForm(Form):
    username = simple.StringField('Username',
        validators=[
            validators.DataRequired(message=''),
            validators.Length(min=6, max=16, message=''),
            validators.Regexp(regex="[0-9a-zA-Z]{6,16}", message='')
        ],
        widget=widgets.TextInput(),
        render_kw={"class": "form-control",
                   "placeholder": "Please enter username"}
    )
    password = simple.PasswordField('Password',
        validators=[
            validators.DataRequired(message=''),
            validators.Length(min=6, max=16, message=''),
            validators.Regexp(regex="[0-9a-zA-Z]{6,16}", message='')
        ],
        widget=widgets.PasswordInput(),
        render_kw={"class": "form-control",
                   "placeholder": "Please enter password"}

    )
    remember = BooleanField('remember me')
    submit = simple.SubmitField(
        label="login",
        render_kw={"class": "btn btn-success"}
    )
class ModifypasswordForm(Form):
    password  = simple.PasswordField(
        validators=[
            validators.DataRequired(message='密码不能为空'),
            validators.Length(min=6, message='用户名长度必须大于%(min)d'),
            validators.Regexp(regex="[0-9a-zA-Z]{6,}", message='密码不允许使用特殊字符')
        ],
        widget=widgets.PasswordInput(),
        render_kw={'class': 'form-control',
                   "placeholder": "please enter password"}
    )
    RepeatPassword = simple.PasswordField(
        validators=[
            validators.DataRequired(message='密码不能为空'),
            validators.Length(min=6, message='密码长度必须大于%(min)d'),
            validators.Regexp(regex="[0-9a-zA-Z]{6,}", message='密码不允许使用特殊字符'),
            validators.EqualTo("password", message="两次密码输入必须一致")
        ],
        widget=widgets.PasswordInput(),
        render_kw={'class': 'form-control',"placeholder": "please enter password again"}
    )
class AuthenticationForm(Form):
    username = simple.StringField(
        # label='注册用户：',
        validators=[
            validators.DataRequired(message='Username cannot be empty'),
            validators.Length(min=6, max=18, message='用户名长度必须大于%(min)d且小于%(max)d')
        ],
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control',
                   "placeholder": "please enter username"}
    )
    email = simple.StringField(
        validators=[DataRequired(), Email(), Length(1, 254)],
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control',
                   "placeholder": "please enter your email"}
    )
@app.route('/register', methods=['GET', 'POST'])
def Register():
    if request.method == 'GET':
        RetForm = RegisterForm()
        return render_template('register.html', form=RetForm)
    else:
        RetForm = RegisterForm(formdata=request.form)
        if RetForm.validate():
            db = pymysql.connect(host='localhost',
                                 user='root',
                                 passwd='123456',
                                 database='test',
                                 port=3303
                                 )
            print(RetForm.data)
            cursor = db.cursor()
            sql="SELECT * FROM account where username='%s' or email='%s'"%(str(RetForm.data["username"]),str(RetForm.data["email"]))
            cursor.execute(sql)
            if len(cursor.fetchall())>=1:
                tkinter.messagebox.showinfo('Notification', 'This username has been registered')
                return redirect('http://127.0.0.1:5000/register')
            else:
             sql = 'INSERT INTO account(username,password,email) VALUES("%s","%s","%s")' % (
                RetForm.data["username"],generate_password_hash(RetForm.data["password"]),generate_password_hash(RetForm.data["email"]))
             cursor.execute(sql)
            # commit
             db.commit()
             db.close()
             tkinter.messagebox.showinfo('Notification', 'Registration success')
             return redirect('http://127.0.0.1:5000/login')
        else:
            print(RetForm.errors)
            return render_template('register.html', form=RetForm)
@app.route("/login", methods=['GET', 'POST'])
def Login():
 if session['username']!='':
        tkinter.messagebox.showinfo('Warning', 'You are already logged in !')
        return redirect('http://127.0.0.1:5000/search')
 else:
    if request.method == 'GET':
        RetForm = LoginForm()
        return render_template('login.html', form=RetForm)
    else:
        RetForm = LoginForm(formdata=request.form)
        if RetForm.validate():
            db = pymysql.connect(host='localhost',
                                 user='root',
                                 passwd='123456',
                                 database='test',
                                 port=3303
                                 )
            temp = RetForm.data
            cursor = db.cursor()
            sql="SELECT password FROM account WHERE username='%s'"%str(temp['username'])
            try:
                # 执行sql语句
                cursor.execute(sql)
                results = cursor.fetchall()
                if check_password_hash(results[0][0],temp["password"]):
                    db.commit()
                    db.close()
                    session['username']=temp['username']
                    return redirect('http://127.0.0.1:5000/search')
                else:
                    db.commit()
                    db.close()
                    tkinter.messagebox.showinfo('Warning', 'Incorrect username or password')
                    return redirect('http://127.0.0.1:5000/login')
            except:
                # 如果发生错误则回滚
                traceback.print_exc()
                db.rollback()
            # 关闭数据库连接
            db.commit()
            db.close()
        return redirect('http://127.0.0.1:5000/login')
@app.route("/search", methods=['GET', 'POST'])
def search():
 if session['username']!='':
    Property_1 ='Density'
    Property_2 = 'Specific volume'
    Class = "!=''"
    db = pymysql.connect(user='root', host='localhost', passwd='123456', db='polyinfodatabase', port=3303)
    cursor = db.cursor()
    sql = "SELECT `" + Property_1 + "` FROM all_data where `" + Property_1 + "`!='' and `" + Property_2 + "`!=''"
    sql1 = "SELECT `" + Property_2 + "` FROM all_data where `" + Property_1 + "`!='' and `" + Property_2 + "`!=''"
    sql2 = "SELECT `" + 'ID' + "` FROM all_data where `" + Property_1 + "`!='' and `" + Property_2 + "`!=''"
    sql3 = "SELECT `" + 'CU Formula' + "` FROM all_data where `" + Property_1 + "`!='' and `" + Property_2 + "`!=''"
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.execute(sql1)
    data1 = cursor.fetchall()
    cursor.execute(sql2)
    data2 = cursor.fetchall()
    cursor.execute(sql3)
    data3 = cursor.fetchall()
    prop_1 = []
    prop_2 = []
    prop_3 = []
    prop_4 = []
    for item in data:
        prop_1.append(float(item[0]))
    for item in data1:
        prop_2.append(float(item[0]))
    for item in data2:
        prop_3.append(str(item[0]))
    for item in data3:
        prop_4.append(str(item[0]))
    for i in range(0, len(data2)):
        prop_4[i] = prop_3[i] + " " + prop_4[i]
    trace0 = Scatter(
        x=prop_1,
        y=prop_2,
        mode='markers',
        text=prop_4,
        marker=dict(
            color=prop_2,
            colorscale='hsv',
            showscale=True
        )
    )
    layout = go.Layout(
        title='Search result',
        xaxis={'title': Property_1},
        yaxis={'title': Property_2}
    )
    data_1 = [trace0]
    fig = go.Figure(data=data_1, layout=layout)
    plotly.offline.plot(fig, filename=r'F:\webdatabase\app\static\img\basic-line.html', auto_open=False)
    db.commit()
    db.close()
    return render_template('search.html',content=prop_3)
 else:
     tkinter.messagebox.showinfo('Warning', 'Please log in to your account first')
     return render_template('http://127.0.0.1:5000/login')
@app.route("/search_type", methods=['GET','POST'])
def search_type():
 if session['username']!='':
    if request.method == 'GET':
        return render_template('search.html')
    else:
     Property_1 = request.form.get("p_prop1_name")
     Property_2=request.form.get("p_prop2_name")
     Property_1_min=request.form.get('p_prop1_min')
     Property_1_max=request.form.get('p_prop1_max')
     Property_2_min=request.form.get('p_prop2_min')
     Property_2_max=request.form.get('p_prop2_max')
     if(Property_1_max==''):
         Property_1_max=math.pow(10,20)
     if(Property_2_max==''):
         Property_2_max=math.pow(10,20)
     if(Property_1_min==''):
         Property_1_min=-math.pow(10,20)
     if(Property_2_min==''):
         Property_2_min=-math.pow(10,20)
     if(request.form.get('p_class')=='not specified'):
        Class="!=''"
     else:
        Class=" like '%"+request.form.get('p_class')+"%'"
     db = pymysql.connect(user='root', host='localhost', passwd='123456', db='polyinfodatabase',port=3303)
     cursor = db.cursor()
     sql = "SELECT `"+Property_1+"` FROM all_data where `"+Property_1+"`!='' and `"+Property_2+"`!='' and Type"+Class+" and `"+Property_2+"`>="+str(Property_2_min)+" and `"+Property_2+"`<="+str(Property_2_max)+" and `"+Property_1+"`>="+str(Property_1_min)+" and `"+Property_1+"`<="+str(Property_1_max)
     sql1= "SELECT `"+Property_2+"` FROM all_data where `"+Property_1+"`!='' and `"+Property_2+"`!='' and Type"+Class+" and `"+Property_2+"`>="+str(Property_2_min)+" and `"+Property_2+"`<="+str(Property_2_max)+" and `"+Property_1+"`>="+str(Property_1_min)+" and `"+Property_1+"`<="+str(Property_1_max)
     sql2 = "SELECT `" + 'ID' + "` FROM all_data where `" + Property_1 + "`!='' and `" + Property_2 + "`!='' and Type" + Class + " and `" + Property_2 + "`>=" + str(Property_2_min) + " and `" + Property_2 + "`<=" + str(Property_2_max) + " and `" + Property_1 + "`>=" + str(Property_1_min) + " and `" + Property_1 + "`<=" + str(Property_1_max)
     sql3 = "SELECT `" + 'CU Formula' + "` FROM all_data where `" + Property_1 + "`!='' and `" + Property_2 + "`!='' and Type" + Class + " and `" + Property_2 + "`>=" + str(Property_2_min) + " and `" + Property_2 + "`<=" + str(Property_2_max) + " and `" + Property_1 + "`>=" + str(Property_1_min) + " and `" + Property_1 + "`<=" + str(Property_1_max)
     cursor.execute(sql)
     data=cursor.fetchall()
     cursor.execute(sql1)
     data1 = cursor.fetchall()
     cursor.execute(sql2)
     data2 = cursor.fetchall()
     cursor.execute(sql3)
     data3 = cursor.fetchall()
     prop_1 = []
     prop_2 = []
     prop_3=[]
     prop_4=[]
     for item in data:
         prop_1.append(float(item[0]))
     for item in data1:
         prop_2.append(float(item[0]))
     for item in data2:
         prop_3.append(str(item[0]))
     for item in data3:
         prop_4.append(str(item[0]))
     for i in range(0,len(data2)):
         prop_4[i]=prop_3[i]+" "+prop_4[i]
     trace0 =Scatter(
         x=prop_1,
         y=prop_2,
         mode='markers',
         text=prop_4,
         marker=dict(
             color=prop_2,
             colorscale='hsv',
             showscale=True
         )
     )
     layout=go.Layout(
         title='Search result',
         xaxis={'title': Property_1},
         yaxis={'title': Property_2}
     )
     data_1 = [trace0]
     fig=go.Figure(data=data_1,layout=layout)
     plotly.offline.plot(fig, filename=r'F:\webdatabase\app\static\img\basic-line.html', auto_open=False)
     db.commit()
     db.close()
     return render_template('search.html',content=prop_3)
 else:
     tkinter.messagebox.showinfo('Warning', 'Please log in to your account first')
     return render_template('http://127.0.0.1:5000/login')
@app.route("/c",methods=['GET','POST'])
def compare():
  if session['username']!='':
    db = pymysql.connect(user='root', host='localhost', passwd='123456', db='polyinfodatabase', port=3303)
    cursor = db.cursor()
    compare=[]
    for i in range(1,5):
        if request.form.get('compare'+str(i)) !=None:
             compare.append(request.form.get('compare'+str(i)))
    show_data=[]
    link=[]
    for item in compare:
      temp = []
      sql="SELECT * FROM all_data WHERE ID='%s'"%item
      cursor.execute(sql)
      data = cursor.fetchall()
      for i in range(0,len(data[0])):
         temp.append(data[0][i])
      show_data.append(temp)
      if data[0][0][0]=='B':
          link.append("/static/img/2D.png")
      else:
         page="https://polymer.nims.go.jp/PoLyInfo/images/Polymer/CU/2D/"+str(data[0][0][1])+str(data[0][0][2])+"/U"+str(data[0][0][1:])+".png"
         link.append(page)
    column=['ID','Name','CU Formula','Density','Specific volume','Crystallization kinetics','Crystallization temp.','Glass transition temp.','Heat of crystallization','Heat of fusion','Thermal decomposition','Linear expansion coefficient','Melting temp.','Specific heat capacity (Cp)','Specific heat capacity (Cv)','Thermal conductivity','Thermal diffusivity','Volume expansion coefficient','Contact angle','Gas diffusion coefficient (D)','Gas permeability coefficient (P)','Gas solubility coefficient (S)','Hansen parameter delta-d(dispersive component)','Hansen parameter delta-h(hydrogen bonding component)','Hansen parameter delta-p(polar component)','Interfacial tension','Solubility parameter','Surface tension','Water absorption','Water vapor transmission','Diffusion coefficient','Intrinsic viscosity [eta]','Non solvent','Second virial coefficient','Sedimentation coefficient','Solvent','Dynamic tensile properties','Elongation at break','Elongation at yield','Fiber tensile modulus','Fiber tensile stress (strength) at break','Tensile modulus','Tensile stress(strength) at break','Tensile stress(strength) at yield','Charpy impact','Izod impact','Rockwell hardness','Shore hardness','Dielectric breakdown voltage','Dielectric const.(DC)','Dielectric dispersion','Electric conductivity','Surface resistivity','Volume resistivity','Refractive index','Stress-optical coefficient','Type','Formula weight(FW)']
    return render_template('search_results.html',content=column,content2=show_data,content3=link,x=len(column),y=len(show_data))
  else:
      tkinter.messagebox.showinfo('Warning', 'Please log in to your account first')
      return redirect('http://127.0.0.1:5000/login')
@app.route("/", methods=['GET', 'POST'])
def first_page():
    session['username'] = ''
    return redirect('http://127.0.0.1:5000/login')
@app.route('/Authentication',methods=['GET','POST'])
def Authentication():
  try:
    if request.method == 'GET':
        RetForm = AuthenticationForm()
        return render_template('Authentication.html', form=RetForm)
    else:
        RetForm = AuthenticationForm(formdata=request.form)
        if RetForm.validate():
            temp = RetForm.data
            db = pymysql.connect(user='root', host='localhost', passwd='123456', db='test', port=3303)
            cursor = db.cursor()
            sql = "SELECT email FROM account WHERE username='%s'" % str(temp['username'])
            cursor.execute(sql)
            if check_password_hash(cursor.fetchall()[0][0],str(temp['email'])):
                    db.commit()
                    db.close()
                    session['username']=temp['username']
                    return redirect('http://127.0.0.1:5000/change_password')
            else:
                    db.commit()
                    db.close()
                    tkinter.messagebox.showinfo('Warning', 'incorrect username or email')
                    return redirect('http://127.0.0.1:5000/Authentication')
        else:
            tkinter.messagebox.showinfo('Warning', 'Invalid input!')
            return render_template('Authentication.html', form=RetForm)
  except:
   session['username'] = ''
   return redirect('http://127.0.0.1:5000/login')
@app.route('/change_password',methods=['GET','POST'])
def change_password():
  try:
    if session['username']=='':
        tkinter.messagebox.showinfo('Warning', 'Please log in to your account first !')
        return redirect('http://127.0.0.1:5000/login')
    else:
        if request.method == 'GET':
            RetForm = ModifypasswordForm()
            return render_template('change_password.html', form=RetForm)
        else:
            RetForm = ModifypasswordForm(formdata=request.form)
            if RetForm.validate():
                temp = RetForm.data
                db = pymysql.connect(user='root', host='localhost', passwd='123456', db='test', port=3303)
                cursor = db.cursor()
                sql="UPDATE account set password='%s' WHERE username='%s'"%(generate_password_hash(temp['password']),session['username'])
                cursor.execute(sql)
                db.commit()
                db.close()
                session['username']=''
                tkinter.messagebox.showinfo('Notification', 'You have reset your password')
                return redirect('http://127.0.0.1:5000/login')
            else:
                tkinter.messagebox.showinfo('Warning', 'Invalid input!')
                return render_template('change_password.html', form=RetForm)
  except:
      session['username']=''

      return redirect('http://127.0.0.1:5000/login')
if __name__ == '__main__':
    app.run()