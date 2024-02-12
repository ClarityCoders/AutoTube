from flask import Flask,render_template,request,redirect
from main import stuff
from utils.upload_video import getid
app = Flask(__name__,template_folder="./html")
app.secret_key="secret"
# some login system related stuffs
def checklogin(username,password):
    with open("ssfile.txt") as f:
        db = eval(f.read())
    for users in db:
        if username == users['uname'] and password == users['passwd']:
            return True
        else:
            pass
    return False

def add_login_info(username, password):
    with open('ssfile.txt') as f:
        page = eval(f.read())
    lst={"uname":username,"passwd":password}
    page.append(lst)
    with open('ssfile.txt',"w") as f:
        f.write(str(page))
#flask part for login and registration
        
#registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        add_login_info(username, password)
        return redirect('/')
    return render_template('register.html')

#login
@app.route('/',methods=['GET','POST'])
def index():
    if request.method== 'POST':
        uname=request.form.get('username')
        passwd=request.form.get('password')
        if checklogin(uname,passwd):
            return redirect('/home')
        else:
            with open("html/lip.html")as f:
                return f.read().replace("</p>","<br>Wrong username or password.</p>")
    return render_template("lip.html")
#process
@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        title1 = request.form.get('title')
        description1= request.form.get('description')
        tags1 = request.form.get('tags')
        privacy1 = request.form.get('privacy')
        subreddit1 = request.form.get('subreddit')
        stuff(title1,description1,tags1,privacy1,subreddit1)
        return redirect("/completed")

    return render_template("index.html")

#actual work is done here 
@app.route('/completed')
def processing():
    with open("html/processing.html") as f:
        page = f.read()
    try:
        rpl=getid()
        return page.replace("vida",rpl)
    except:
        return page.replace('<a href="https://www.youtube.com/watch?v=vida">vida</a>',"your channel<br>(Note quota has exceeded, please try again after 24 hrs or purchase higher plans for quota.)")
app.run(host="127.0.0.1",port=81)