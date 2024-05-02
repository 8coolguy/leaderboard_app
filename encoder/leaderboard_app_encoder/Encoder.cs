using System;
using Dynastream.Fit;

namespace EncoderFunctions;

public static class Encoder{
    static public void CreateTimeBasedActivity()
        {
            const double TwoPI = Math.PI * 2.0;
            const double SemicirclesPerMeter = 107.173;
            const string FileName = "ActivityEncodeRecipe.fit";

            var messages = new List<Mesg>();

            // The starting timestamp for the activity
            var startTime = new Dynastream.Fit.DateTime(System.DateTime.UtcNow);

            // Timer Events are a BEST PRACTICE for FIT ACTIVITY files
            var eventMesgStart = new EventMesg();
            eventMesgStart.SetTimestamp(startTime);
            eventMesgStart.SetEvent(Event.Timer);
            eventMesgStart.SetEventType(EventType.Start);
            messages.Add(eventMesgStart);

            // Create the Developer Id message for the developer data fields.
            var developerIdMesg = new DeveloperDataIdMesg();
            // It is a BEST PRACTICE to reuse the same Guid for all FIT files created by your platform
            byte[] appId = new Guid("00010203-0405-0607-0809-0A0B0C0D0E0F").ToByteArray();
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
            var timestamp = new Dynastream.Fit.DateTime(startTime);

            // Create one hour (3600 seconds) of Record data
            for (uint i = 0; i <= 3600; i++)
            {
                // Create a new Record message and set the timestamp
                var recordMesg = new RecordMesg();
                recordMesg.SetTimestamp(timestamp);

                // Fake Record Data of Various Signal Patterns
                recordMesg.SetDistance(i); // Ramp
                recordMesg.SetSpeed(1); // Flatline
                recordMesg.SetHeartRate((byte)((Math.Sin(TwoPI * (0.01 * i + 10)) + 1.0) * 127.0)); // Sine
                recordMesg.SetCadence((byte)(i % 255)); // Sawtooth
                recordMesg.SetPower((ushort)((i % 255) < 127 ? 150 : 250)); // Square
                recordMesg.SetAltitude((float)Math.Abs(((double)i % 255.0) - 127.0)); // Triangle
                recordMesg.SetPositionLat(0);
                recordMesg.SetPositionLong((int)Math.Round(i * SemicirclesPerMeter));

                // Add a Developer Field to the Record Message
                var hrDevField = new DeveloperField(hrFieldDescMesg, developerIdMesg);
                recordMesg.SetDeveloperField(hrDevField);
                hrDevField.SetValue((byte)((Math.Sin(TwoPI * (0.01 * i + 10)) + 1.0) * 127.0)); // Sine

                // Write the Rercord message to the output stream
                messages.Add(recordMesg);

                // Increment the timestamp by one second
                timestamp.Add(1);
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
}