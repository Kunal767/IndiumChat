var socketio = io.connect('https://' + document.domain + ':' + location.port);

const messages = document.getElementById('messages');

messages.scrollTop = messages.scrollHeight;

var recname = document.getElementById('receivername');
var recstatus = document.getElementById('receiverstatus');
var sendername = document.getElementById('sendername').innerHTML;

windowlocation = window.location.href.split("/")

recname.innerHTML = decodeURI(windowlocation[windowlocation.length - 1]);
receivername = decodeURI(windowlocation[windowlocation.length - 1]);

const createmyMsg = (name, msg, datetime) => {
    const content = `
    <div class="mymsg">
        <p class="msgname">${name}</p>
        ${msg}<br>
        <p class="chatdate">${datetime}</p>
    </div>`;
    messages.innerHTML += content;
};

const createOppoMsg = (name, msg, datetime) => {
    const content = `
    <div class="oppomsg">
        <p class="msgname">${name}</p>
        ${msg}<br>
        <p class="chatdate">${datetime}</p>
    </div>`;
    messages.innerHTML += content;
};

socketio.on("message", (data) => {

    if (data.name == receivername) {
        createOppoMsg(data.name, data.msg, data.datetime)
        messages.scrollTop = messages.scrollHeight;
    } else {
        createmyMsg(data.name, data.msg, data.datetime)
        messages.scrollTop = messages.scrollHeight;
    }
});

const sendMessage = () => {
    var msg = document.getElementById('msg');
    if (msg.value == "") {
        return;
    };
    socketio.emit("message", {message: msg.value, receiver: receivername, sender: sendername});
    msg.value = "";
};