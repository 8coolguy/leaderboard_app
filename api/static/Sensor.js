class Sensor{
    constructor(type,socket,id){
        if(type==0){
            var service = "heart_rate";
            var characteristic = "heart_rate_measurement";
        }
        else if(type==1){
            var service = "cycling_speed_and_cadence";
            var characteristic = "csc_measurement";
        }
        this.socket = socket;
        this.type = type;
        this.service = service;
        this.characteristic = characteristic;
        this.id=id;
    }
    connect(){
        console.log('Requesting Bluetooth Device...');
        return new Promise((res,rej)=>{
        navigator.bluetooth.requestDevice({filters: [{services: [this.service]}]})
        .then(device => {
            console.log('Connecting to GATT Server...');
            this.name = device.name;
            return device.gatt.connect();
        })
        .then(server => {
            console.log('Getting Service...');
            return server.getPrimaryService(this.service);
        })
        .then(service => {
            console.log('Getting Characteristics...');
        
            // Get all characteristics that match this UUID.
            return service.getCharacteristics(this.characteristic);
        
            // Get all characteristics.
            return service.getCharacteristics();
        })
        .then(characteristics => {
            //console.log('> Characteristics: ' + characteristics.map(c => c.uuid).join('\n' + ' '.repeat(19)));
            this.deviceCharacteristic = characteristics[0];
            this.deviceCharacteristic.startNotifications().then(_ => {
                this.deviceCharacteristic.addEventListener('characteristicvaluechanged',this.handler().bind(this));
                res();
            });

        })
        .catch(error => {
            rej();
            console.log('Argh! ' + error);
        });
    })
    }
    handler(){
        if(this.type==0)
            return this.heartRateChange;
        else if(this.type==1)
            return this.cScChange
    }
    heartRateChange(event){
        const value = event.target.value;
        const currentHeartRate = value.getUint8(1);
        console.log('currentHeartRate:', Date.now().toString(), currentHeartRate);
        this.socket.emit("activity_tick",{[Date.now().toString()]:{heartRate:currentHeartRate}});
    }
    cScChange(event){
        var offset = 0;
        var temp;

        const values = event.target.value;
        const flags = values.getUint8(offset,true);
        offset += 1; // UINT8 = 8 bits = 1 byte
    
        // we have to check the flags' 0th bit to see if C1 field exists 
        if ((flags & 1) != 0) {
            temp = values.getUint32(offset,true);
            var deltaRev = temp - this.cumulativeWheelRevolutions;
            this.cumulativeWheelRevolutions = temp;
            offset += 4; // UINT32 = 32 bits = 4 bytes
            
            temp = values.getUint16(offset,true);
            var deltaWheelTime = temp - this.lastWheelEventTime;
            this.lastWheelEventTime = temp;
            offset += 2; // UINT16 = 16 bits = 2 bytes
        }
    
        // we have to check the flags' 1st bit to see if C2 field exists 
        if ((flags & 2) != 0) {
            temp = values.getUint16(offset,true);
            var deltaCrankRevs = temp - this.cumulativeCrankRevolutions;
            this.cumulativeCrankRevolutions = temp;
            offset += 2;
            
            temp = values.getUint16(offset,true);
            var deltaCrankTime = temp - this.lastCrankEventTime;
            this.lastCrankEventTime = temp;
            offset += 2;
        }
        
        const speed = deltaRev/deltaWheelTime*60*1024*60*0.001310472;
        const cadence = deltaCrankRevs/deltaCrankTime*60*1024;

        
        // if(speed!=NaN) console.log('speed:',Date.now().toString(),speed);
        // if(cadence!=NaN) console.log('cadence:',Date.now().toString(),cadence);
        // if(speed!=NaN)socket.emit("activity_tick",{[Date.now().toString()]:{speed:speed}});
        // if(cadence!=NaN)socket.emit("activity_tick",{[Date.now().toString()]:{cadence:cadence}});
    }
}
