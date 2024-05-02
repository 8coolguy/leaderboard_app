using EncoderFunctions;
using System;
using FireSharp;
using FireSharp.Config;
using FireSharp.Interfaces;
using FireSharp.Response;
using Dynastream.Fit;

IFirebaseConfig fc = new FirebaseConfig(){
    AuthSecret = Environment.GetEnvironmentVariable("apiKey"),
    BasePath = Environment.GetEnvironmentVariable("databaseURL")
};

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

var summaries = new[]
{
    "Freezing"
};

app.MapGet("/weatherforecast/{rid}/{uid}", (string rid,string uid) =>
{
   
    var startTime = new Dynastream.Fit.DateTime(System.DateTime.UtcNow);
    IFirebaseClient client=new FireSharp.FirebaseClient(fc);
    
    FirebaseResponse response = client.Get("rooms/current_rooms/1/name");
    String res =response.ResultAs<String>();
    Console.WriteLine(rid,uid);
    Console.WriteLine(res);
    Console.WriteLine(startTime.ToString());
    Encoder.CreateTimeBasedActivity();
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
