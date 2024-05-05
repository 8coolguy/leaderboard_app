using System;
using Dynastream.Fit;

namespace EncoderFunctions;

public class Encoder{
    

    static public void CreateTimeBasedActivity(dynamic timestamps,Dynastream.Fit.DateTime startTime)
        {
            const double TwoPI = Math.PI * 2.0;
            const double SemicirclesPerMeter = 107.173;
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

            // Create the Developer Data Field Descriptions
            var doughnutsFieldDescMesg = new FieldDescriptionMesg();
            doughnutsFieldDescMesg.SetDeveloperDataIndex(0);
            doughnutsFieldDescMesg.SetFieldDefinitionNumber(0);
            doughnutsFieldDescMesg.SetFitBaseTypeId(FitBaseType.Float32);
            doughnutsFieldDescMesg.SetFieldName(0, "Doughnuts Earned");
            doughnutsFieldDescMesg.SetUnits(0, "doughnuts");
            doughnutsFieldDescMesg.SetNativeMesgNum(MesgNum.Session);
            messages.Add(doughnutsFieldDescMesg);

            FieldDescriptionMesg hrFieldDescMesg = new FieldDescriptionMesg();
            hrFieldDescMesg.SetDeveloperDataIndex(0);
            hrFieldDescMesg.SetFieldDefinitionNumber(1);
            hrFieldDescMesg.SetFitBaseTypeId(FitBaseType.Uint8);
            hrFieldDescMesg.SetFieldName(0, "Heart Rate");
            hrFieldDescMesg.SetUnits(0, "bpm");
            hrFieldDescMesg.SetNativeFieldNum(RecordMesg.FieldDefNum.HeartRate);
            hrFieldDescMesg.SetNativeMesgNum(MesgNum.Record);
            messages.Add(hrFieldDescMesg);

            // Every FIT ACTIVITY file MUST contain Record messages
            Dynastream.Fit.DateTime timestamp =new Dynastream.Fit.DateTime(System.DateTime.UtcNow);
            float distance =0;
            float speed =0;
            byte heartRate = 0;
            byte cadence = 0;
            foreach (var dino in timestamps){
                Console.WriteLine($"{dino.Name}");
                timestamp = ToDateTime(dino.Name);
                var recordMesg = new RecordMesg();
                Console.WriteLine($"{timestamp.GetDateTime()}");
                recordMesg.SetTimestamp(timestamp);
                foreach (var dino1 in dino){
                    foreach (var dino2 in dino1){
                        // Create a new Record message and set the timestamp
                        if(dino2.Name=="heartRate" &&dino2.Value > 0){
                            heartRate = (byte)dino2.Value;
                            // recordMesg.SetHeartRate();
                            Console.WriteLine($"{(byte)dino2.Value}");
                        } // Sine
                        if(dino2.Name=="speed" && dino2.Value > 0){
                            recordMesg.SetSpeed((float)(dino2.Value)*1609.34f);
                            Console.WriteLine($"{(float)dino2.Value}");
                        }
                        if(dino2.Name=="cadence" && dino2.Value > 0){
                            recordMesg.SetCadence((byte)(dino2.Value));
                            Console.WriteLine($"{(byte)dino2.Value}");
                        }
                        if(dino2.Name=="distance" && dino2.Value > 0){
                            distance = (float)(dino2.Value)*1609.34f;
                            Console.WriteLine($"{(float)dino2.Value}");
                        }

                        // Fake Record Data of Various Signal Patterns
                         // Ramp // Sawtooth
                        
                        

                        // Add a Developer Field to the Record Message
                        // var hrDevField = new DeveloperField(hrFieldDescMesg, developerIdMesg);
                        // recordMesg.SetDeveloperField(hrDevField);
                        // hrDevField.SetValue((byte)((Math.Sin(TwoPI * (0.01 * i + 10)) + 1.0) * 127.0)); // Sine

                        // Write the Rercord message to the output stream
                        
                    }
                }
                // recordMesg.SetPower(100);
                recordMesg.SetHeartRate(heartRate);
                // recordMesg.SetDistance(distance); // Square
                messages.Add(recordMesg);
            }


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
            sessionMesg.SetSport(Sport.Cycling);
            sessionMesg.SetSubSport(SubSport.Generic);
            sessionMesg.SetFirstLapIndex(0);
            sessionMesg.SetNumLaps(1);

            // Add a Developer Field to the Session message
            var doughnutsEarnedDevField = new DeveloperField(doughnutsFieldDescMesg, developerIdMesg);
            doughnutsEarnedDevField.SetValue(sessionMesg.GetTotalElapsedTime() / 1200.0f);
            sessionMesg.SetDeveloperField(doughnutsEarnedDevField);
            messages.Add(sessionMesg);

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
public class Metric  {
    public string ?cadence { get; set;}
    public string ?heartRate { get; set;}
    public string ?speed { get; set;}
};
public class Tick{
    public Dictionary<string,Metric> metric { get; set;}
};