using WhedNamespace;

var builder = WebApplication.CreateBuilder(args);

Console.WriteLine(builder.Configuration.GetConnectionString("DefaultConnection"));

// Add services to the container
builder.Services.AddSingleton<DatabaseContext>(provider =>
{
    var logger = provider.GetRequiredService<ILogger<DatabaseContext>>();
    return new DatabaseContext(builder.Configuration.GetConnectionString("DefaultConnection"), logger);
});
builder.Services.AddControllers();
builder.Services.AddSwaggerGen();

// Build and configure the app
var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(c =>
    {
        c.SwaggerEndpoint("/swagger/v1/swagger.json", "WHED API");
    });
}

//app.UseHttpsRedirection();
app.UseAuthorization();

app.MapControllers();

// Run the app in a try-catch block
try
{
    Console.WriteLine($"Environment: {app.Environment.EnvironmentName}");

    app.Run();

}
catch (Exception ex)
{
    Console.WriteLine($"Application startup failed: {ex.Message}");
    Console.Out.Flush();
}
