var socket;
var started=false;
//Global Variable for the stopwatch
var startTime;
var stopWatchInterval;
var elapsedPause=0;
var mile = 0;
var devices =[];
var cumulativeWheelRevolutions = 0;
var lastWheelEventTime = 0;
var cumulativeCrankRevolutions = 0;
var lastCrankEventTime = 0;

var temp;

const x_pos = 100;//x pos of circle
const y_pos = 100;//y pos of circle
const r = 50;//radius od circle
const m = 10;//mod of small circle


window.addEventListener("time_change",(event) => {drawCircle(mile);mile+=.01;});
window.addEventListener("start",(arg) => {drawCircle(mile);mile+=.01;});
function connectSocket(){
    socket=io({autoconnect:false});
    socket.connect();
    socket.on("connect", function(res) {
        socket.on('response', (msg) => {
            console.log(msg);
        });
        socket.emit("user_join", "Hello");
    })
    socket.on("start", (arg) => {
        startTime =arg;
        startClock();
    });
    socket.on("end", (arg) => {
        window.location.href = "google.com";
    });
}

window.addEventListener("beforeunload", function (e) {
    var confirmationMessage = "\o/";
    (e || window.event).returnValue = confirmationMessage;
    socket.emit("user_leave");
    return confirmationMessage;                            //Webkit, Safari, Chrome
  });
window.onload=connectSocket;


function startActivity(){
    socket.emit("activity_start",Date.now().toString());
}
function stopActivity(){
    socket.emit("activity_end",Date.now().toString());
}

function addDevice(e) {
    e.preventDefault();
    const s =new Sensor(e.target[0].value,socket,devices.length);
    while(e.target.firstChild && e.target.removeChild(e.target.firstChild));
    e.target.setHTMLUnsafe(`<div>Connecting...</div>`)
    devices.push(s);
    const button = "<button hx-boost=\"true\" hx-get=\"remove\" hx-target=\"closest form\" hx-swap=\"outerHTML\" class=\"bg-red-500 hover:bg-red-700 text-white font-bold h-5 w-5 rounded\" type=\"button\">x</button>";
    s.connect().then(()=>{
        while(e.target.firstChild && e.target.removeChild(e.target.firstChild));
        e.target.setHTMLUnsafe(`<div>${s.name}</div>${button}`)
    })
}

/**
 * Updates the activity clock
 */
function updateClock(){
    var currentTime=Date.now();
    var elapsedTime = currentTime - startTime; // calculate elapsed time in milliseconds
    var seconds = Math.floor(elapsedTime / 1000) % 60; // calculate seconds
    var minutes = Math.floor(elapsedTime / 1000 / 60) % 60; // calculate minutes
    var hours = Math.floor(elapsedTime / 1000 / 60 / 60); // calculate hours
    var time = pad(hours)+":"+pad(minutes)+":"+pad(seconds);
    document.getElementById("stopwatch").innerHTML=time;
    window.dispatchEvent(new Event("time_change"));
}
/**
 * Starts the Activty Clock
 */
function startClock(){
    if(!stopWatchInterval){
        
        //startTime=Date.now()-elapsedPause;
        stopWatchInterval=setInterval(updateClock,1000);
    }
}
/**
 * Stops activity Clokc
 */
function stopClock(){
    if(stopWatchInterval){
        clearInterval(stopWatchInterval); // stop the interval
        elapsedPause = Date.now() - startTime; // calculate elapsed paused time
        stopWatchInterval = null;
    }
}
/**
 * Restes the clock
 */
function resetClock(){
    if(stopWatchInterval){
        stopClock();
    } // stop the interval
    elapsedPause = 0;
    document.getElementById("stopwatch").innerHTML="00:00:00";
}


/**
 * Circle Visual for Distance
 */
function drawCircle(miles){
    const canvas = document.querySelector("canvas");
    miles = Math.floor(miles * 100) / 100;
    

    if (!canvas.getContext)
        return;
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    var theta = miles * (2 * Math.PI);

    ctx.beginPath();
    ctx.arc(x_pos, y_pos, r, 0, 2 * Math.PI);
    ctx.stroke();

    ctx.fillStyle = "#008000"; //green
    ctx.beginPath();
    ctx.arc(x_pos+r*Math.sin(theta),y_pos-r*Math.cos(theta), r/m, 0, 2 * Math.PI);
    ctx.stroke();
    ctx.fill();

    ctx.font = "24px Arial";
    ctx.textAlign = 'center';
    ctx.fillStyle = 'black';
    ctx.fillText(miles, x_pos, y_pos+6);//add one fourth of the text size
}
/**
 * Pads a zero
 */
function pad(i){
    if(i<10){
        return "0" + i.toString()
    }else{
        return i.toString()
    }
}

/**
 * Deletes a current form element.
 */
function clearForm(event){
}