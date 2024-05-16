var socket;
//Global Variable for the stopwatch
var startTime;
var stopWatchInterval;
var elapsedPause=0;
var mile = 0;
var devices =[];


const x_pos = 100;//x pos of circle
const y_pos = 100;//y pos of circle
const r = 50;//radius od circle
const m = 10;//mod of small circle


window.addEventListener("time_change",(event) =>{ 
    miles+=event.detail;
    console.log(miles); 
    document.getElementById("distance").innerHTML = miles;
    socket.emit("leaderboard", "Hello");
    // drawCircle(miles);
});

function connectSocket(){
    socket=io({autoconnect:false});
    socket.connect();
    socket.on("connect", function(res) {
        socket.emit("user_join", "Hello");
    })
	socket.on('response', (msg) => {
	    console.log(msg);
       		socket.emit("leaderboard");
	});
    socket.on("start", (arg) => {
        startTime =arg;
        startClock();
    });
    socket.on("end", (arg) => {
        window.location.href = arg;
    });
    socket.on("distance", (arg) => {
        miles = arg;
        // drawCircle(miles);
    });
    socket.on("leaderboard",(arg)=>{
        //update sticks
        drawStick(arg);
        console.log(arg);
    })
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
/**
 * Function draws stick figure bikes
 */
function drawStick(array){
    const canvas = document.getElementById("canvas");
    if (!canvas.getContext)
        return;
    
    const ctx = canvas.getContext("2d");
    var space = canvas.width/6;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const mean = (array.reduce((a, b) => a + b) / array.length);
    const std = getStandardDeviation (array);
    console.log(array);
    console.log(mean,std);
    
    for(let i =  array.length-1; i >= 0; i--){
        var score = ((array[i]-mean)/std);
        if (isNaN(score)) score = 0;
        if(i==0)
                ctx.strokeStyle = "green";
        else
                ctx.strokeStyle = "black";
        
        var x = canvas.width/2+score*space;
        var y = canvas.height/2;
        var r = 10;
        var gap = 25;
        var bb = 12;
        var seatPost = 17;
        var top = 8;
        var handle = 5;
        var stickLength = 15;
        var stickArm = 10;
        var stickLegY = 10;
        var stickLegX = 3;

        ctx.beginPath();
        ctx.arc(x, y, r, 0, 2 * Math.PI);
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(x-gap, y, r, 0, 2 * Math.PI);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(x-gap,y);
        ctx.lineTo(x-gap+bb,y)
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(x-gap+bb,y);
        ctx.lineTo(x-gap+bb,y-seatPost);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(x-gap+bb,y);
        ctx.lineTo(x-gap+bb+top,y-seatPost);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(x-gap+bb,y-seatPost);
        ctx.lineTo(x-gap,y);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(x-gap+bb,y-seatPost);
        ctx.lineTo(x-gap+bb+top,y-seatPost);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(x-gap+bb+top,y-seatPost);
        ctx.lineTo(x,y);
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(x-gap+bb+top, y-seatPost-handle, handle, 0,Math.PI/2);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(x-gap+bb,y-seatPost);
        ctx.lineTo(x-gap+bb,y-seatPost-stickLength);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(x-gap+bb,y-seatPost);
        ctx.lineTo(x-gap+bb-stickLegX,y-seatPost+stickLegY);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(x-gap+bb,y-seatPost);
        ctx.lineTo(x-gap+bb+stickLegX,y-seatPost+stickLegY);
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(x-gap+bb, y-seatPost-stickLength-r/4, r/4, 0, 2 * Math.PI);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(x-gap+bb-stickLength/2,y-seatPost-stickLength/2);
        ctx.lineTo(x-gap+bb+stickLength/2,y-seatPost-stickLength/2);
        ctx.stroke();
    }
}

/**
 * Functions that generated background for the bikes
 */
function generateBackground(){
    //Do something
}
/*
*Std Dev Code by = Foxcode on StackOverflow
*/
function getStandardDeviation (array) {
    const n = array.length;
    const mean = array.reduce((a, b) => a + b) / n;
    return Math.sqrt(array.map(x => Math.pow(x - mean, 2)).reduce((a, b) => a + b) / n);
}
