using EncoderFunctions;
using System.Collections.Generic; 
using System;
using Newtonsoft.Json;
using Dynastream.Fit;
using FireSharp.Extensions;
using Firebase.Database;
using Firebase.Database.Query;
using Nest;
using Microsoft.AspNetCore.Authentication;

using FireSharp;
using FireSharp.Config;
using FireSharp.Interfaces;
using FireSharp.Response;

Console.WriteLine("Server Start..."); 
var auth = Environment.GetEnvironmentVariable("apiKey"); // your app secret
// var firebaseClient = new FirebaseClient(
//   Environment.GetEnvironmentVariable("databaseURL"),
//   new FirebaseOptions
//   {
//     AuthTokenAsyncFactory = () => Task.FromResult(auth) 
//   });

var builder = WebApplication.CreateBuilder(args);
// Add services to the container.
// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();

IFirebaseConfig fc = new FirebaseConfig(){
    AuthSecret = Environment.GetEnvironmentVariable("apiKey"),
    BasePath = Environment.GetEnvironmentVariable("databaseURL")
};

app.MapGet("/weatherforecast/{rid}/{uid}",  (string rid,string uid) =>
{
    Console.WriteLine(rid);
    Console.WriteLine(uid);
    // var startTime = new Dynastream.Fit.DateTime(System.DateTime.UtcNow);
    IFirebaseClient client=new FireSharp.FirebaseClient(fc);
    FirebaseResponse response = client.Get("rooms/past_rooms/"+rid+"/players/"+uid);
    var json = response.Body;
    FirebaseResponse response2 = client.Get("rooms/past_rooms/"+rid+"/start");
    var startTime = response2.Body;
    
    dynamic result = JsonConvert.DeserializeObject(json);
    
    

    // var name = firebaseClient
    //     .Child("rooms")
    //     .Child("past_rooms")
    //     .Child(rid)
    //     .Child("name")
    //     .
    // Console.WriteLine(name);
       
    // var dinos = await firebaseClient
    //     .Child("rooms")
    //     .Child("past_rooms")
    //     .Child(rid)
    //     .Child("players")
    //     .Child(uid)
    //     .OnceAsync<Encoder>();
    //     // .Once<Encoder.Ticks>();
    // Console.WriteLine(dinos.Count);
    
    
    
    
    //Console.WriteLine(startTime.ToString());
    Encoder.CreateTimeBasedActivity(result,Encoder.ToDateTime(startTime));
    // var forecast =  Enumerable.Range(1, 5).Select(index =>
    //     new WeatherForecast
    //     (
    //         DateOnly.FromDateTime(System.DateTime.Now.AddDays(index)),
    //         Random.Shared.Next(-20, 55),
    //         summaries[Random.Shared.Next(summaries.Length)]
    //     ))
    //     .ToArray();
    return Results.File("/Users/8coolguy/Documents/leaderboard_app/encoder/leaderboard_app_encoder/ActivityEncodeRecipe.fit");
    // return "success";
})
.WithName("GetWeatherForecast")
.WithOpenApi();

app.Run();

record WeatherForecast(DateOnly Date, int TemperatureC, string? Summary)
{
    public int TemperatureF => 32 + (int)(TemperatureC / 0.5556);
}
