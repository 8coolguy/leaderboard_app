console.log("Hello World");
var socket;
var started=false;
//Global Variable for the stopwatch
var startTime;
var stopWatchInterval;
var elapsedPause=0;
var mile = 0;

const x_pos = 100;//x pos of circle
const y_pos = 100;//y pos of circle
const r = 50;//radius od circle
const m = 10;//mod of small circle


window.addEventListener("time_change",(event) => {drawCircle(mile);mile+=.01;});
function connectSocket(){
    socket=io({autoconnect:false});
    socket.connect();
    socket.on("connect", function(res) {
        socket.on('response', (msg) => {
            console.log(msg);
        });
        socket.emit("user_join", "Hello");
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
    //delete this button from room
    startClock();
}
function heartRateChange(event){
    const value = event.target.value;
    const currentHeartRate = value.getUint8(1);
    // console.log('currentHeartRate:', currentHeartRate,Date.now().toString());
    socket.emit("activity_tick",{[Date.now().toString()]:{heartRate:currentHeartRate}});
}
function onClick() {
    console.log(socket);
    console.log('Requesting Bluetooth Device...');
    navigator.bluetooth.requestDevice({filters: [{services: ["heart_rate"]}]})
    .then(device => {
      console.log('Connecting to GATT Server...');
      return device.gatt.connect();
    })
    .then(server => {
        console.log('Getting Service...');
        return server.getPrimaryService("heart_rate");
    })
    .then(service => {
        console.log('Getting Characteristics...');
      
        // Get all characteristics that match this UUID.
        return service.getCharacteristics("heart_rate_measurement");
      
        // Get all characteristics.
        return service.getCharacteristics();
    })
    .then(characteristics => {
        console.log(characteristics[0])
        console.log('> Characteristics: ' + characteristics.map(c => c.uuid).join('\n' + ' '.repeat(19)));
        this.characteristic = characteristics[0];
        return this.characteristic.startNotifications().then(_ => {
            this.characteristic.addEventListener('characteristicvaluechanged',this.heartRateChange.bind(this));
        });
    })
    .catch(error => {
        console.log('Argh! ' + error);
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
    window.dispatchEvent(new Event("time_change"));
}
/**
 * Starts the Activty Clock
 */
function startClock(){
    if(!stopWatchInterval){
        startTime=Date.now()-elapsedPause;
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
