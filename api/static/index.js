console.log("Hello World");
var socket;
var started=false;
//Global Variable for the stopwatch
var startTime;
var stopWatchInterval;
var elapsedPause=0;

function connectSocket(){
    socket=io({autoconnect:false});
    socket.connect();
    socket.on("connect", function() {
        socket.emit("user_join", "Hello");
    })
    
}
window.onload=connectSocket;

function startActivity(){
    socket.emit("activity_start",Date.now().toString());
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
