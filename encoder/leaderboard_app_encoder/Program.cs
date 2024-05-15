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
    AuthSecret = Environment.GetEnvironmentVariable("APIKEY"),
    BasePath = Environment.GetEnvironmentVariable("DATABASEURL")
};

app.MapGet("/weatherforecast/{rid}/{uid}",  (string rid,string uid) =>
{
    IFirebaseClient client = new FireSharp.FirebaseClient(fc);
    FirebaseResponse response = client.Get("rooms/past_rooms/"+rid+"/players/"+uid);
    var json = response.Body;
    if(json.Length <=4) return Results.NotFound();
    FirebaseResponse response2 = client.Get("rooms/past_rooms/"+rid+"/start");
    var startTime = response2.Body;
    if(startTime.Length <=4) return Results.NotFound();
    dynamic result = JsonConvert.DeserializeObject(json);
    Encoder.CreateTimeBasedActivity(result,Encoder.ToDateTime(startTime),0.0f);
    return Results.File(System.Environment.CurrentDirectory+"/ActivityEncodeRecipe.fit");
    
})
.WithName("GetWeatherForecast")
.WithOpenApi();

app.Run();