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

window.addEventListener("beforeunload", function () {
    if (socket && socket.connected) {
        socket.emit("user_leave");
    }
});
window.onload = function() {
    connectSocket();
    // Draw terrain + clouds immediately so the canvas isn't blank
    var canvas = document.getElementById("canvas");
    if (canvas && canvas.getContext) {
        var ctx = canvas.getContext("2d");
        drawTerrain(ctx, canvas.width, canvas.height);
        drawClouds(ctx, canvas.width, canvas.height, 0);
    }
};


function startActivity(){
    socket.emit("activity_start",Date.now().toString());
}
function stopActivity(){
    socket.emit("activity_end",Date.now().toString());
}

function addDevice(e) {
    e.preventDefault();
    const form = e.target;
    const select = form.querySelector('select');
    const sensorType = parseInt(select.value);

    if (!Sensor.isAvailable()) {
        form.innerHTML = `<div class="text-xs text-red-500 p-2">Web Bluetooth not supported. Use Chrome.</div>`;
        return;
    }

    const s = new Sensor(sensorType, socket, devices.length);
    form.innerHTML = `<div class="text-xs text-slate-500 p-2">Connecting…</div>`;
    devices.push(s);

    s.connect()
        .then((deviceName) => {
            form.innerHTML = `<div class="flex items-center justify-between">
                <span class="text-xs text-slate-700">${deviceName}</span>
                <button onclick="this.closest('form').remove();devices.pop();" class="text-slate-300 hover:text-red-500 w-5 h-5 rounded text-xs transition-colors" type="button">&times;</button>
            </div>`;
        })
        .catch((err) => {
            var msg = err.message || 'Connection failed';
            if (msg.length > 120) msg = msg.substring(0, 120) + '…';
            form.innerHTML = `<div class="text-xs text-red-600 p-2">${msg} <button onclick="this.closest('form').remove()" class="underline ml-1 text-red-400 hover:text-red-600">Dismiss</button></div>`;
            devices.pop();
        });
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

    // Always draw terrain, even if no players yet
    drawTerrain(ctx, canvas.width, canvas.height);

    // Draw scrolling clouds — offset tied to total distance ridden
    var cloudOffset = (array && array.length > 0) ? (array[0] || 0) : 0;
    drawClouds(ctx, canvas.width, canvas.height, cloudOffset);

    // Guard against empty array — reduce() throws on empty array
    if (!array || array.length === 0) {
        return;
    }

    const mean = array.reduce((a, b) => a + b, 0) / array.length;
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
        var y = canvas.height * 0.72;
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
 * Draws a sparse cycling backdrop — ground, mountains, bumps.
 * Rendered once into an offscreen canvas and cached.
 * Clouds are drawn separately in drawClouds() since they scroll.
 */
var _terrainCache = null;

function drawTerrain(ctx, w, h) {
    if (_terrainCache && _terrainCache.width === w && _terrainCache.height === h) {
        ctx.drawImage(_terrainCache, 0, 0);
        return;
    }

    var off = document.createElement('canvas');
    off.width = w;
    off.height = h;
    var c = off.getContext('2d');

    var groundY = h * 0.78;

    // Background fill
    c.fillStyle = '#f8fafc';
    c.fillRect(0, 0, w, h);

    // Mountains — simple layered triangles
    c.fillStyle = '#e2e8f0';
    var peaks = [
        {x: 0.12, h: 0.28},
        {x: 0.28, h: 0.18},
        {x: 0.42, h: 0.35},
        {x: 0.58, h: 0.22},
        {x: 0.72, h: 0.30},
        {x: 0.88, h: 0.16},
    ];
    for (var i = 0; i < peaks.length; i++) {
        var mx = w * peaks[i].x;
        var mh = h * peaks[i].h;
        var mw = 70 + (i % 2) * 30;
        c.beginPath();
        c.moveTo(mx - mw, groundY);
        c.lineTo(mx, groundY - mh);
        c.lineTo(mx + mw, groundY);
        c.closePath();
        c.fill();
    }

    // Darker closer mountains
    c.fillStyle = '#cbd5e1';
    var peaks2 = [
        {x: 0.20, h: 0.15},
        {x: 0.50, h: 0.20},
        {x: 0.80, h: 0.12},
    ];
    for (var i = 0; i < peaks2.length; i++) {
        var mx = w * peaks2[i].x;
        var mh = h * peaks2[i].h;
        var mw = 50 + (i % 2) * 20;
        c.beginPath();
        c.moveTo(mx - mw, groundY);
        c.lineTo(mx, groundY - mh);
        c.lineTo(mx + mw, groundY);
        c.closePath();
        c.fill();
    }

    // Ground
    c.fillStyle = '#e2e8f0';
    c.fillRect(0, groundY, w, h - groundY);

    // Ground line
    c.strokeStyle = '#cbd5e1';
    c.lineWidth = 1;
    c.beginPath();
    c.moveTo(0, groundY);
    c.lineTo(w, groundY);
    c.stroke();

    // Small ground bumps
    c.fillStyle = '#cbd5e1';
    var bumps = [0.15, 0.4, 0.65, 0.9];
    for (var i = 0; i < bumps.length; i++) {
        var bx = w * bumps[i];
        var bw = 14 + (i % 3) * 8;
        var bh = 3 + (i % 2) * 2;
        c.beginPath();
        c.ellipse(bx, groundY, bw / 2, bh, 0, Math.PI, 0);
        c.fill();
    }

    // Sparse grass dashes
    c.strokeStyle = '#cbd5e1';
    c.lineWidth = 1;
    var dashes = [0.05, 0.18, 0.32, 0.48, 0.6, 0.75, 0.88];
    for (var i = 0; i < dashes.length; i++) {
        var dx = w * dashes[i];
        var dh = 6 + (i % 3) * 4;
        c.beginPath();
        c.moveTo(dx, groundY);
        c.lineTo(dx, groundY - dh);
        c.stroke();
    }

    _terrainCache = off;
    ctx.drawImage(off, 0, 0);
}

/**
 * Draws scrolling clouds. Offset is driven by total distance so they drift as you ride.
 */
function drawClouds(ctx, w, h, offset) {
    var groundY = h * 0.78;
    ctx.fillStyle = '#e2e8f0';

    // Cloud positions repeat every 600px; offset makes them scroll
    var cloudDefs = [
        {x: 0.08, y: 0.15, s: 1.0},
        {x: 0.28, y: 0.22, s: 0.7},
        {x: 0.52, y: 0.10, s: 1.3},
        {x: 0.74, y: 0.18, s: 0.8},
        {x: 0.90, y: 0.12, s: 0.6},
    ];

    var scroll = (offset * 20) % w;

    for (var i = 0; i < cloudDefs.length; i++) {
        var d = cloudDefs[i];
        var cx = ((d.x * w - scroll) % w + w) % w;
        var cy = h * d.y;
        var s = d.s;

        // Simple pill-shaped cloud
        var cw = 30 * s;
        var ch = 10 * s;
        ctx.beginPath();
        ctx.ellipse(cx, cy, cw, ch, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.ellipse(cx - cw * 0.5, cy + ch * 0.3, cw * 0.6, ch * 0.7, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.ellipse(cx + cw * 0.4, cy + ch * 0.2, cw * 0.5, ch * 0.6, 0, 0, Math.PI * 2);
        ctx.fill();
    }
}
/*
*Std Dev Code by = Foxcode on StackOverflow
*/
function getStandardDeviation (array) {
    const n = array.length;
    const mean = array.reduce((a, b) => a + b) / n;
    return Math.sqrt(array.map(x => Math.pow(x - mean, 2)).reduce((a, b) => a + b) / n);
}
