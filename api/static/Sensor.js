class Sensor {
    constructor(type, socket, id) {
        // Standard Bluetooth GATT UUIDs (full 128-bit)
        if (type == 0) {
            this.serviceUUID = 0x180D;          // Heart Rate
            this.characteristicUUID = 0x2A37;   // Heart Rate Measurement
        } else if (type == 1) {
            this.serviceUUID = 0x1816;          // Cycling Speed and Cadence
            this.characteristicUUID = 0x2A5B;   // CSC Measurement
        }
        this.socket = socket;
        this.type = type;
        this.id = id;
        this.device = null;
        this.server = null;
        this.deviceCharacteristic = null;
        // State tracking for CSC calculations
        this.cumulativeWheelRevolutions = 0;
        this.lastWheelEventTime = 0;
        this.cumulativeCrankRevolutions = 0;
        this.lastCrankEventTime = 0;
    }

    /**
     * Check if Web Bluetooth is available in this browser.
     */
    static isAvailable() {
        return !!navigator.bluetooth;
    }

    connect() {
        const label = this.type == 0 ? 'Heart Rate Monitor' : 'Speed/Cycling Sensor';
        console.log(`[Sensor] Requesting ${label}...`);

        if (!Sensor.isAvailable()) {
            return Promise.reject(new Error('Web Bluetooth not available'));
        }

        // Build request options: try exact filter first, fallback to any device
        const options = {
            filters: [{ services: [this.serviceUUID] }],
            optionalServices: [this.serviceUUID]  // CRITICAL: Android needs this to access GATT
        };

        return navigator.bluetooth.requestDevice(options)
            .then(device => {
                this.device = device;
                this.name = device.name || 'Unknown device';
                console.log(`[Sensor] Paired with "${this.name}", connecting to GATT...`);

                // Handle unexpected disconnection
                device.addEventListener('gattserverdisconnected', () => {
                    console.warn(`[Sensor] "${this.name}" disconnected.`);
                    this._onDisconnect();
                });

                return device.gatt.connect();
            })
            .then(server => {
                this.server = server;
                console.log('[Sensor] GATT connected, getting service...');
                return server.getPrimaryService(this.serviceUUID);
            })
            .then(service => {
                console.log('[Sensor] Service found, getting characteristic...');
                return service.getCharacteristic(this.characteristicUUID);
            })
            .then(characteristic => {
                this.deviceCharacteristic = characteristic;
                console.log('[Sensor] Characteristic found, starting notifications...');
                return characteristic.startNotifications();
            })
            .then(() => {
                const handler = this._getHandler().bind(this);
                this.deviceCharacteristic.addEventListener('characteristicvaluechanged', handler);
                console.log(`[Sensor] "${this.name}" ready and listening.`);
                return this.name;
            })
            .catch(error => {
                const msg = this._formatError(error, label);
                console.error('[Sensor]', msg);
                throw new Error(msg);
            });
    }

    /**
     * Disconnect and clean up the sensor.
     */
    disconnect() {
        if (this.device && this.device.gatt.connected) {
            this.device.gatt.disconnect();
        }
        this.device = null;
        this.server = null;
        this.deviceCharacteristic = null;
    }

    _onDisconnect() {
        this.deviceCharacteristic = null;
        this.server = null;
        // Clear the display values
        if (this.type == 0) {
            document.getElementById('hr').innerHTML = '--';
        } else {
            document.getElementById('speed').innerHTML = '--';
            document.getElementById('cadence').innerHTML = '--';
        }
    }

    _getHandler() {
        return this.type == 0 ? this._heartRateChange : this._cscChange;
    }

    _heartRateChange(event) {
        const value = event.target.value;
        const flags = value.getUint8(0);
        const is16Bit = flags & 1;
        let hr;
        if (is16Bit) {
            hr = value.getUint16(1, true);
        } else {
            hr = value.getUint8(1);
        }
        this.socket.emit('activity_tick', {
            [Date.now().toString()]: { heartRate: hr }
        });
        document.getElementById('hr').innerHTML = hr;
    }

    _cscChange(event) {
        let offset = 0;
        const values = event.target.value;
        const flags = values.getUint8(offset, true);
        offset += 1;

        let speed = NaN, cadence = NaN, distance = NaN;

        // Wheel revolution data (C1)
        if (flags & 1) {
            const wheelRevs = values.getUint32(offset, true);
            offset += 4;
            const wheelTime = values.getUint16(offset, true);
            offset += 2;

            const deltaRev = wheelRevs - (this.cumulativeWheelRevolutions || wheelRevs);
            const deltaTime = wheelTime - (this.lastWheelEventTime || wheelTime);

            this.cumulativeWheelRevolutions = wheelRevs;
            this.lastWheelEventTime = wheelTime;

            if (deltaTime > 0) {
                // Standard wheel circumference: 2.105m (700c x 23mm tire)
                // rev * circumference(m) * (1024 / deltaTime) * 3.6 = km/h → /1.609 = mph
                distance = deltaRev * 0.001310472; // miles per rev
                speed = (deltaRev / deltaTime) * 1024 * 2.105 * 2.23694; // mph
            }
        }

        // Crank revolution data (C2)
        if (flags & 2) {
            const crankRevs = values.getUint16(offset, true);
            offset += 2;
            const crankTime = values.getUint16(offset, true);
            offset += 2;

            const deltaCrankRevs = crankRevs - (this.cumulativeCrankRevolutions || crankRevs);
            const deltaCrankTime = crankTime - (this.lastCrankEventTime || crankTime);

            this.cumulativeCrankRevolutions = crankRevs;
            this.lastCrankEventTime = crankTime;

            if (deltaCrankTime > 0) {
                cadence = (deltaCrankRevs / deltaCrankTime) * 1024 * 60; // rpm
            }
        }

        if (!isNaN(distance)) {
            window.dispatchEvent(new CustomEvent('time_change', { detail: distance }));
        }

        if (!isNaN(speed)) {
            this.socket.emit('activity_tick', {
                [Date.now().toString()]: { speed: speed, distance: distance }
            });
            document.getElementById('speed').innerHTML = Math.round(speed * 100) / 100;
        }
        if (!isNaN(cadence)) {
            this.socket.emit('activity_tick', {
                [Date.now().toString()]: { cadence: cadence }
            });
            document.getElementById('cadence').innerHTML = Math.round(cadence * 100) / 100;
        }
        if (isNaN(speed) && isNaN(cadence)) {
            document.getElementById('speed').innerHTML = '--';
            document.getElementById('cadence').innerHTML = '--';
        }
    }

    /**
     * Translate Web Bluetooth errors into human-readable messages.
     */
    _formatError(error, label) {
        const msg = String(error.message || error);

        if (msg.includes('User cancelled') || msg.includes('cancelled')) {
            return 'Pairing cancelled.';
        }
        if (msg.includes('Bluetooth adapter not available') || msg.includes('Bluetooth off')) {
            return 'Bluetooth is turned off. Please enable Bluetooth on your device.';
        }
        if (msg.includes('No Services') || msg.includes('Service not found')) {
            return `"${this.name || 'Device'}" doesn't appear to be a ${label}. ` +
                'Make sure your device supports the Bluetooth Heart Rate or Cycling Speed/Cadence profile.';
        }
        if (msg.includes('No Characteristics')) {
            return `"${this.name || 'Device'}" connected but didn\'t provide ${label} data. ` +
                'Check that the sensor is in pairing/transmit mode.';
        }
        if (msg.includes('GATT operation failed') || msg.includes('disconnected')) {
            return `Lost connection to "${this.name || 'device'}". Move closer and try again.`;
        }
        if (msg.includes('SecurityError') || msg.includes('NotAllowedError')) {
            return 'Bluetooth permission denied. On Android, Chrome needs Location permission to scan for Bluetooth devices. ' +
                'Go to Settings → Apps → Chrome → Permissions → Location → Allow.';
        }
        if (msg.includes('NotFoundError') || msg.includes('no device')) {
            return `No ${label} found nearby. Make sure your device is in pairing mode and within range. ` +
                'Try restarting Bluetooth on both devices.';
        }
        if (msg.includes('NetworkError') || msg.includes('GATT server')) {
            return `Could not connect to "${this.name || 'device'}". Try turning Bluetooth off and on, then pair again.`;
        }
        return `Couldn't connect: ${msg}`;
    }
}
