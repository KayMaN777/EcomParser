using BlazorDownloadFile;
using Blazorise;
using Microsoft.AspNetCore.Components;
using Microsoft.AspNetCore.Components.Web;
using MudBlazorTemplates2.Data;
using MudBlazor.Services;
using Blazorise.Bootstrap5;
using Blazorise.Charts;

var builder = WebApplication.CreateBuilder(args);

// Добавление сервисов в контейнер
builder.Services.AddRazorPages();
builder.Services.AddServerSideBlazor();
builder.Services.AddSingleton<WeatherForecastService>();
builder.Services.AddMudServices();
builder.Services.AddBlazorDownloadFile(); // Для загрузки файлов
builder.Services
    .AddBlazorise()
    .AddBootstrap5Providers(); // Подключаем Bootstrap

builder.Services.AddHttpClient("ServerAPI", client =>
{
    client.BaseAddress = new Uri(builder.Configuration["BaseAddress"]); // Укажите базовый адрес API
});
builder.Configuration.AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);
// Настройка CORS (если нужно)
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAllOrigins",
        builder =>
        {
            builder.AllowAnyOrigin() // Разрешить все домены
                .AllowAnyMethod() // Разрешить все HTTP-методы (GET, POST и т.д.)
                .AllowAnyHeader(); // Разрешить все заголовки
        });
});

var app = builder.Build();

// Использование CORS (если нужно)
app.UseCors("AllowAllOrigins");

// Настройка конвейера HTTP-запросов
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error");
    app.UseHsts(); // Включение HSTS в production
}

app.UseHttpsRedirection();
app.UseStaticFiles();
app.UseRouting();

app.MapBlazorHub();
app.MapFallbackToPage("/_Host");

app.Run();