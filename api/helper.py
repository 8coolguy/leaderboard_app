def getStopWatch():
    return '''
            <div id="stopwatch">00:00:00</div>
            <div class="flex">
                <button class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded" type="button" onclick="startActivity()">Start Activity</button>
                <button class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded" type="button" onclick="startActivity()">Stop Activity</button>
            </div>
            <div class="flex">
                <button class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded" type="button" onclick="stopClock()">Stop</button>
                <button class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded" type="button" onclick="startClock()">Start</button>
                <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" type="button" onclick="resetClock()">Lap/Reset</button>
            </div>'''
            # make the lap/reset button change based on what state it is.2