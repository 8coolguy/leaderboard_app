console.log("Hello World");
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
function cScChange(event){
    const values = event.target.value;
    // console.log("-> "+(event.target.value.getUint8(0, true)>>> 0).toString(2)); //characteristics flags
    var offset = 0;
    const flags = values.getUint8(offset,true);
    console.log(flags);
    offset += 1; // UINT8 = 8 bits = 1 byte

    // we have to check the flags' 0th bit to see if C1 field exists 
    if ((flags & 1) != 0) {
        temp = values.getUint32(offset,true);
        var deltaRev = temp - cumulativeWheelRevolutions;
        cumulativeWheelRevolutions = temp;
        offset += 4; // UINT32 = 32 bits = 4 bytes
        
        temp = values.getUint16(offset,true);
        var deltaWheelTime = temp - lastWheelEventTime;
        lastWheelEventTime = temp;
        offset += 2; // UINT16 = 16 bits = 2 bytes
    }

    // we have to check the flags' 1st bit to see if C2 field exists 
    if ((flags & 2) != 0) {
        temp = values.getUint16(offset,true);
        var deltaCrankRevs = temp - cumulativeCrankRevolutions;
        cumulativeCrankRevolutions = temp;
        offset += 2;
        
        temp = values.getUint16(offset,true);
        var deltaCrankTime = temp - lastCrankEventTime;
        lastCrankEventTime = temp;
        offset += 2;
    }
    
    // console.log("Delta Wheel Revs: ",deltaRev);
    // console.log("Delta Wheel Time: ",deltaWheelTime);
    console.log("Delta Wheel Time: ",deltaRev/deltaWheelTime*60*1024*60*0.001310472);//.,002109
    console.log("Delta Crank Time: ",deltaCrankRevs/deltaCrankTime*60*1024);
    
    console.log("0 Cum_Wheel_Rev :", cumulativeWheelRevolutions);
    console.log("1 LastwheelUpdte :", lastWheelEventTime);
    console.log("2 Cum. Cranks :", cumulativeCrankRevolutions);
    console.log("3 LastCrankEventTime :", lastCrankEventTime);
    // console.log('currentSpeed:', currentSpeed,Date.now().toString());
    //socket.emit("activity_tick",{[Date.now().toString()]:{heartRate:currentHeartRate}});
}
async function addDevice(e) {
    e.preventDefault();
    
    console.log(devices);
    const s =new Sensor(e.target[0].value,socket,devices.length);
    devices.push(s);
    s.connect().then(()=>{
        while(e.target.firstChild && e.target.removeChild(e.target.firstChild));
        e.target.setHTML(`<div>${s.name}</div>`)
    })
    
    //s.name
   
    
}

function onClick2() {
    console.log('Requesting Bluetooth Device...');
    navigator.bluetooth.requestDevice({filters: [{services: ["cycling_speed_and_cadence"]}]})
    .then(device => {
      console.log('Connecting to GATT Server...');
      return device.gatt.connect();
    })
    .then(server => {
        console.log('Getting Service...');
        return server.getPrimaryService("cycling_speed_and_cadence");
    })
    .then(service => {
        console.log('Getting Characteristics...');
      
        // Get all characteristics that match this UUID.
        return service.getCharacteristics("csc_measurement");
      
        // Get all characteristics.
        return service.getCharacteristics();
    })
    .then(characteristics => {
        // console.log(characteristics[0]);
        //console.log('> Characteristics: ' + characteristics.map(c => c.uuid).join('\n' + ' '.repeat(19)));
        this.characteristic = characteristics[0];
        return this.characteristic.startNotifications().then(_ => {
            this.characteristic.addEventListener('characteristicvaluechanged',this.cScChange.bind(this));
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
    console.log(event);
}