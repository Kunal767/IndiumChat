from flask import Flask, session, redirect, render_template, request
from flask_socketio import join_room, leave_room, send, SocketIO
import json
import random, string
from datetime import datetime
from operator import itemgetter

app = Flask(__name__)
app.config["SECRET_KEY"] = "thereisaghostoverhere@98267"
iosocket = SocketIO(app)


def read_members_file():
    with open("static/members.json", 'r') as members_file:
        membersdetails = json.load(members_file)
    return membersdetails

def write_members_file(newdetails):
    with open("static/members.json", 'w') as members_file:
        json.dump(newdetails, members_file)

def readroomfile():
    with open("static/rooms.json", 'r') as roomfile:
        roomdetails = json.load(roomfile)
    return roomdetails

def writeroomfile(newdetails):
    with open("static/rooms.json", 'w') as roomfile:
        json.dump(newdetails, roomfile)

def generate_random_id():
    allletters = []
    for values in string.ascii_letters:
        allletters.append(values)
    random.shuffle(allletters)
    randomid = ""
    for value in allletters:
        randomid = randomid+value
    return randomid[:10]

@app.route("/", methods=['GET', 'POST'])
def home():
    try:
        if session['username']:
            return redirect("/members")
        else:
            return render_template("index.html")
    except KeyError:
        return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        members = read_members_file()
        if username in members.keys():
            if password == members.get(username)['Password']:
                session['username'] = username
                return redirect("/members")
        return render_template("login.html", error_code=1)
    else:
        return render_template("login.html")

@app.route("/members", methods=['GET', 'POST'])
def room():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        members = read_members_file()

        if username in members.keys():
            return render_template("index.html", error_code=1)

        members[username] = {"Password": password, "Messages": [], "lastSeen": "New User"}
        write_members_file(members)
        session['username'] = username

        members = read_members_file()
        return render_template("members.html", members=members)
    else:
        if session['username']:
            members = read_members_file()
            return render_template("members.html", members=members)
        else:
            return redirect("/")

@app.route("/chat/<string:member_name>", methods=['POST', 'GET'])
def member_name(member_name):
    if session['username']:
        roomdetails = readroomfile()
        roomcode = ""
        for rm in roomdetails["activerooms"]:
            if session['username'] in rm and member_name in rm:
                roomcode = rm
                break
        if roomcode == "":
            roomcode = session['username']+member_name
            roomdetails["activerooms"].append(roomcode)
            writeroomfile(roomdetails)
        session['room'] = roomcode
        membersfile = read_members_file()
        allminechats = membersfile[session['username']]['Messages']
        previousminechats = []
        for minechat in allminechats:
            if minechat["to_user"] == member_name:
                previousminechats.append(minechat)
        alltheirchats = membersfile[member_name]['Messages']
        for theirchat in alltheirchats:
            if theirchat["to_user"] == session['username']:
                previousminechats.append(theirchat)
        sortedchats = sorted(previousminechats, key=itemgetter("datetime"))
        opponentstatus = membersfile[member_name]["lastSeen"]
        return render_template("chat.html", prechats=sortedchats, opponent=member_name, status=opponentstatus)


@iosocket.on("connect")
def connect(auth):
    membersfile = read_members_file()
    membersfile[session['username']]['lastSeen'] = "Online"
    write_members_file(membersfile)
    mutualroom = session.get("room")
    username = session.get("username")
    if not mutualroom or not username:
        return
    join_room(mutualroom)

@iosocket.on("message")
def message(data):
    mutualroom = session['room']
    sendername = data['sender']
    receivername = data["receiver"]
    msg = data['message']
    currentdatetime = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    msge = {"name": sendername, "msg": msg, "datetime": currentdatetime}
    send(msge, to=mutualroom)

    members = read_members_file()
    newmessage = {"to_user": receivername, "datetime": currentdatetime, "msg": msg}
    specificmember = members[sendername]
    specificmember['Messages'].append(newmessage.copy())
    write_members_file(members)


@iosocket.on("disconnect")
def disconnect():
    membersfile = read_members_file()
    currentdatetime = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    membersfile[session['username']]['lastSeen'] = currentdatetime
    write_members_file(membersfile)
    mutualroom = session.get("room")
    leave_room(mutualroom)
    session.pop('room', None)

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect("/login")

if __name__ == "__main__":
    iosocket.run(app, debug=True)