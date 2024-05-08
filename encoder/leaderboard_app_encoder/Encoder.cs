using System;
using Dynastream.Fit;
using Newtonsoft.Json.Linq;

namespace EncoderFunctions;

public class Encoder{
    static public void CreateTimeBasedActivity(dynamic timestamps,Dynastream.Fit.DateTime startTime,float totalDistance)
        {
            const string FileName = "ActivityEncodeRecipe.fit";
            var messages = new List<Mesg>();

            // Timer Events are a BEST PRACTICE for FIT ACTIVITY files
            var eventMesgStart = new EventMesg();
            eventMesgStart.SetTimestamp(startTime);
            eventMesgStart.SetEvent(Event.Timer);
            eventMesgStart.SetEventType(EventType.Start);
            messages.Add(eventMesgStart);

            // Create the Developer Id message for the developer data fields.
            var developerIdMesg = new DeveloperDataIdMesg();
            // It is a BEST PRACTICE to reuse the same Guid for all FIT files created by your platform
            //New career ideas are worth pursuing.
            byte[] appId = new Guid("95EEBA35-7F36-471A-ACE8-94DFD491B009").ToByteArray();
            for (int i = 0; i < appId.Length; i++)
            {
                developerIdMesg.SetApplicationId(i, appId[i]);
            }
            developerIdMesg.SetDeveloperDataIndex(0);
            developerIdMesg.SetApplicationVersion(110);
            messages.Add(developerIdMesg);

            // Every FIT ACTIVITY file MUST contain Record messages
            Dynastream.Fit.DateTime timestamp=new Dynastream.Fit.DateTime(System.DateTime.Now);
            uint prevTimeStamp = 0;
            float distance =0;
            float speed =0;
            byte heartRate = 0;
            byte cadence = Byte.MinValue;
            // int c =0;
            foreach (var timestampObj in timestamps){
                // c+=1;
                var recordMesg = new RecordMesg();
                timestamp = ToDateTime(timestampObj.Name);
                //code assumes the timestamps are sorted
                if(prevTimeStamp != 0){
                    for(uint i =prevTimeStamp+1; i<timestamp.GetTimeStamp();i++){
                        //Console.WriteLine(i);
                        recordMesg = new RecordMesg();
                        recordMesg.SetTimestamp(new Dynastream.Fit.DateTime(i));
                        recordMesg.SetPower(0);
                        recordMesg.SetSpeed(0f);
                        recordMesg.SetHeartRate(heartRate);
                        recordMesg.SetCadence(Byte.MinValue);
                        recordMesg.SetDistance(distance*.447f);
                        messages.Add(recordMesg);
                    }
                }
                recordMesg = new RecordMesg();
                JObject timestampDetails = timestampObj.First;
                // Console.WriteLine(timestamp.GetTimeStamp());
                var tmp = timestampDetails.GetValue("speed");
                speed = tmp is null ? 0f : (float)tmp;
                tmp = timestampDetails.GetValue("heartRate");
                heartRate = tmp is null ? heartRate : (byte)tmp;
                tmp = timestampDetails.GetValue("distance");
                distance = tmp is null ? distance : (float)tmp;
                tmp = timestampDetails.GetValue("cadence");
                cadence = tmp is null || (float)tmp < 0f ? Byte.MinValue : (byte)tmp;
                // Add a Developer Field to the Record Message
                // var hrDevField = new DeveloperField(hrFieldDescMesg, developerIdMesg);
                // recordMesg.SetDeveloperField(hrDevField);
                // hrDevField.SetValue((byte)((Math.Sin(TwoPI * (0.01 * i + 10)) + 1.0) * 127.0)); // Sine
                // Write the Rercord message to the output stream                        
                
                recordMesg.SetTimestamp(timestamp);
                recordMesg.SetPower(100);
                recordMesg.SetSpeed(speed*.447f);
                recordMesg.SetHeartRate(heartRate);
                recordMesg.SetCadence(cadence);
                recordMesg.SetDistance(distance*.447f);
                messages.Add(recordMesg);
                prevTimeStamp = timestamp.GetTimeStamp();
            }
            // Console.WriteLine(c);

            // Timer Events are a BEST PRACTICE for FIT ACTIVITY files
            var eventMesgStop = new EventMesg();
            eventMesgStop.SetTimestamp(timestamp);
            eventMesgStop.SetEvent(Event.Timer);
            eventMesgStop.SetEventType(EventType.StopAll);
            messages.Add(eventMesgStop);

            // Every FIT ACTIVITY file MUST contain at least one Lap message
            var lapMesg = new LapMesg();
            lapMesg.SetMessageIndex(0);
            lapMesg.SetTimestamp(timestamp);
            lapMesg.SetStartTime(startTime);
            lapMesg.SetTotalElapsedTime(timestamp.GetTimeStamp() - startTime.GetTimeStamp());
            lapMesg.SetTotalTimerTime(timestamp.GetTimeStamp() - startTime.GetTimeStamp());
            messages.Add(lapMesg);

            // Every FIT ACTIVITY file MUST contain at least one Session message
            var sessionMesg = new SessionMesg();
            sessionMesg.SetMessageIndex(0);
            sessionMesg.SetTimestamp(timestamp);
            sessionMesg.SetStartTime(startTime);
            sessionMesg.SetTotalElapsedTime(timestamp.GetTimeStamp() - startTime.GetTimeStamp());
            sessionMesg.SetTotalTimerTime(timestamp.GetTimeStamp() - startTime.GetTimeStamp());
            //sessionMesg.SetTotalDistance(totalDistance*.447f);
            sessionMesg.SetSport(Sport.Cycling);
            sessionMesg.SetSubSport(SubSport.Generic);
            sessionMesg.SetFirstLapIndex(0);
            sessionMesg.SetNumLaps(1);


            // Every FIT ACTIVITY file MUST contain EXACTLY one Activity message
            var activityMesg = new ActivityMesg();
            activityMesg.SetTimestamp(timestamp);
            activityMesg.SetNumSessions(1);
            var timezoneOffset = (int)TimeZoneInfo.Local.BaseUtcOffset.TotalSeconds;
            activityMesg.SetLocalTimestamp((uint)((int)timestamp.GetTimeStamp() + timezoneOffset));
            activityMesg.SetTotalTimerTime(timestamp.GetTimeStamp() - startTime.GetTimeStamp());
            messages.Add(activityMesg);

            WriteActivityFile(messages, FileName, startTime);

        }
    static void WriteActivityFile(List<Mesg> messages, String filename, Dynastream.Fit.DateTime startTime){
        // The combination of file type, manufacturer id, product id, and serial number should be unique.
        // When available, a non-random serial number should be used.
        Dynastream.Fit.File fileType = Dynastream.Fit.File.Activity;
        ushort manufacturerId = Manufacturer.Development;
        ushort productId = 0;
        float softwareVersion = 1.0f;

        Random random = new Random();
        uint serialNumber = (uint)random.Next();

        // Every FIT file MUST contain a File ID message
        var fileIdMesg = new FileIdMesg();
        fileIdMesg.SetType(fileType);
        fileIdMesg.SetManufacturer(manufacturerId);
        fileIdMesg.SetProduct(productId);
        fileIdMesg.SetTimeCreated(startTime);
        fileIdMesg.SetSerialNumber(serialNumber);

        // A Device Info message is a BEST PRACTICE for FIT ACTIVITY files
        var deviceInfoMesg = new DeviceInfoMesg();
        deviceInfoMesg.SetDeviceIndex(DeviceIndex.Creator);
        deviceInfoMesg.SetManufacturer(Manufacturer.Development);
        deviceInfoMesg.SetProduct(productId);
        deviceInfoMesg.SetProductName("leaderboard_app"); // Max 20 Chars
        deviceInfoMesg.SetSerialNumber(serialNumber);
        deviceInfoMesg.SetSoftwareVersion(softwareVersion);
        deviceInfoMesg.SetTimestamp(startTime);

        // Create the output stream, this can be any type of stream, including a file or memory stream. Must have read/write access
        FileStream fitDest = new FileStream(filename, FileMode.Create, FileAccess.ReadWrite, FileShare.Read);

        // Create a FIT Encode object
        Encode encoder = new Encode(ProtocolVersion.V20);

        // Write the FIT header to the output stream
        encoder.Open(fitDest);

        // Write the messages to the file, in the proper sequence
        encoder.Write(fileIdMesg);
        encoder.Write(deviceInfoMesg);

        foreach (Mesg message in messages)
        {
            encoder.Write(message);
        }
        // Update the data size in the header and calculate the CRC
        encoder.Close();
        // Close the output stream
        fitDest.Close();
        Console.WriteLine($"Encoded FIT file {fitDest.Name}");
    }
    private static uint epoch = (uint)(new System.DateTime(1989, 12, 31, 0, 0, 0, DateTimeKind.Utc) - new System.DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc)).TotalSeconds;
    public static Dynastream.Fit.DateTime ToDateTime(string timestamp){
        timestamp = timestamp.Replace("\"","");
        timestamp = timestamp.Substring(0,10);
        uint dateTimeValue = UInt32.Parse(timestamp.Substring(0,10));
        dateTimeValue = dateTimeValue-epoch;
        return new Dynastream.Fit.DateTime(dateTimeValue);
    } 
}