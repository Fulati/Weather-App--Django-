import requests
from django.shortcuts import render, redirect
from .models import City
from .forms import CityForm
from datetime import datetime, timezone, timedelta


def index(request):
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=e3cb235f9230aa02e41407cdbb89219c'

    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            city_name = form.cleaned_data['name']
            # Check if the city already exists in the database
            existing_city = City.objects.filter(name__iexact=city_name).first()
            if existing_city:
                # Delete the previous entry for this city
                existing_city.delete()
            form.save()

    form = CityForm()

    cities = City.objects.all()

    weather_data = []

    for city in cities:
        r = requests.get(url.format(city)).json()

        # Check if the API response contains an error message
        if 'message' in r and r['message'].lower() == 'city not found':
            continue  # Skip this city and move to the next one

        timestamp = r['dt']
        local_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)

        # Adjust local time based on the city's timezone offset
        timezone_offset = timedelta(seconds=r['timezone'])
        local_time += timezone_offset

        city_weather = {
            'local_time': local_time.strftime("%a , %b %d %Y, %I:%M%p"),
            'city': city.name,
            'country': r['sys']['country'],
            'avg_temp': r['main']['temp'],
            'temp_min': r['main']['temp_min'],
            'temp_max': r['main']['temp_max'],
            'humidity': r['main']['humidity'],
            'description': r['weather'][0]['description'],
            'icon': r['weather'][0]['icon'],
        }

        weather_data.append(city_weather)

    weather_data.reverse()

    context = {'weather_data': weather_data, 'form': form}

    return render(request, 'weather/weather.html', context)

def clear_cities(request):
    # Delete all cities from the database
    City.objects.all().delete()
    return redirect('index')  # Redirect back to the index page