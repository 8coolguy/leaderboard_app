using EncoderFunctions;
using Newtonsoft.Json;
using FireSharp.Config;
using FireSharp.Interfaces;
using FireSharp.Response;

Console.WriteLine("Server Start..."); 
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
    IFirebaseClient client=new FireSharp.FirebaseClient(fc);
    FirebaseResponse response = client.Get("rooms/past_rooms/"+rid+"/players/"+uid);
    var json = response.Body;
    FirebaseResponse response2 = client.Get("rooms/past_rooms/"+rid+"/start");
    var startTime = response2.Body;
    FirebaseResponse response3 = client.Get("rooms/past_rooms/"+rid+"/leaderboard/"+uid+"/distance");
    float totalDistance = (float) Convert.ToDouble(response3.Body);

    dynamic result = JsonConvert.DeserializeObject(json);
    Encoder.CreateTimeBasedActivity(result,Encoder.ToDateTime(startTime),totalDistance);
    return Results.File("/Users/8coolguy/Documents/leaderboard_app/encoder/leaderboard_app_encoder/ActivityEncodeRecipe.fit");
    
})
.WithName("GetWeatherForecast")
.WithOpenApi();

app.Run();