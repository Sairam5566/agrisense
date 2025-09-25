document.addEventListener('DOMContentLoaded', () => {
    const weatherForm = document.querySelector('.weather-form');
    const weatherResults = document.querySelector('.weather-results');
    const latInput = document.getElementById('lat');
    const lonInput = document.getElementById('lon');
    const windyIframe = document.getElementById('windy-map');

    // Use server-side API via FastAPI proxy; no API key on client
    const forecastEndpoint = '/api/weather/forecast';

    // Set default coordinates for Jharkhand
    const defaultLat = '23.3441';
    const defaultLon = '85.3096';
    latInput.value = defaultLat;
    lonInput.value = defaultLon;

    // --- Windy map helpers ---
    function buildWindyUrl(lat, lon, overlay) {
        const ov = overlay || (document.querySelector('.overlay-btn.active')?.dataset.overlay) || 'wind';
        return `https://embed.windy.com/embed2.html?lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}&zoom=8&overlay=${encodeURIComponent(ov)}&menu=&message=&marker=&calendar=&pressure=&type=map&location=coordinates&detail=&detailLat=${encodeURIComponent(lat)}&detailLon=${encodeURIComponent(lon)}&metricWind=default&metricTemp=default&radarRange=-1`;
    }

    function updateWindyMap(overlay) {
        if (!windyIframe) return;
        const lat = latInput.value || defaultLat;
        const lon = lonInput.value || defaultLon;
        windyIframe.src = buildWindyUrl(lat, lon, overlay);
    }

    // Bind overlay control buttons (right side of map)
    console.log('Found buttons', document.querySelectorAll('.overlay-btn').length);
    document.querySelectorAll('.overlay-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            console.log('Button clicked', btn.dataset.overlay);
            document.querySelectorAll('.overlay-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            updateWindyMap(btn.dataset.overlay);
        });
    });

    weatherForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const lat = latInput.value;
        const lon = lonInput.value;

        if (lat && lon) {
            await getWeatherData(lat, lon);
            // Update map to match submitted coordinates
            updateWindyMap();
        }
    });

    // Geolocation handler
    const btn = document.getElementById('current-location-btn');
    if (btn && navigator.geolocation) {
        btn.addEventListener('click', () => {
            navigator.geolocation.getCurrentPosition(async (pos) => {
                const { latitude, longitude } = pos.coords;
                latInput.value = latitude.toFixed(4);
                lonInput.value = longitude.toFixed(4);
                await getWeatherData(latitude, longitude);
                updateWindyMap();
            }, (err) => {
                alert('Unable to access your location: ' + err.message);
            });
        });
    }

    async function getWeatherData(lat, lon) {
        weatherResults.innerHTML = '<div class="text-center"><i class="fas fa-spinner fa-spin"></i> Loading...</div>';

        try {
            // Fetch forecast and historical weather data
            try {
                const forecast = await fetchForecast(lat, lon);
                if (forecast.error) throw new Error(forecast.error);
                displayWeather(forecast);
            } catch (error) {
                console.error('Error fetching forecast data:', error);
                weatherResults.innerHTML = `<div class="alert alert-danger">Failed to fetch forecast data. Error: ${error.message}.</div>`;
            }

        } catch (error) {
            console.error('Error fetching weather data:', error);
            weatherResults.innerHTML = `<div class="alert alert-danger">Failed to fetch weather data. Error: ${error.message}. Please check the console for more details.</div>`;
        }
    }

    async function fetchForecast(lat, lon) {
        const url = `${forecastEndpoint}?lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}`;
        const response = await fetch(url);
        if (!response.ok) {
            const errorBody = await response.text();
            console.error('API Error Body (Forecast):', errorBody);
            throw new Error(`HTTP error! status: ${response.status} - ${response.statusText}`);
        }
        return await response.json();
    }


    function displayWeather(forecast) {
        const dailyData = {};
        const getLocalDateString = (date) => {
            // Use a local-timezone based date string for grouping
            return new Date(date.getFullYear(), date.getMonth(), date.getDate()).toISOString().split('T')[0];
        }

        // Group forecast data by local date string
        forecast.forEach(f => {
            const dateKey = getLocalDateString(new Date(f.dt * 1000));
            if (!dailyData[dateKey]) {
                dailyData[dateKey] = [];
            }
            dailyData[dateKey].push(f);
        });

        let tableHtml = '<div class="weather-table-container"><table class="weather-table"><thead><tr>';
        const days = Object.keys(dailyData).sort().slice(0, 7);

        const todayStr = getLocalDateString(new Date());
        const tomorrowDate = new Date();
        tomorrowDate.setDate(tomorrowDate.getDate() + 1);
        const tomorrowStr = getLocalDateString(tomorrowDate);

        // Generate Table Headers
        days.forEach(dayKey => {
            const dayDate = new Date(dailyData[dayKey][0].dt * 1000);
            const dayLabel = dayDate.toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' });
            let finalLabel = dayLabel;
            let thClass = '';

            if (dayKey === todayStr) {
                finalLabel = 'Today';
                thClass = 'today-column';
            } else if (dayKey === tomorrowStr) {
                finalLabel = 'Tomorrow';
            }
            tableHtml += `<th class="${thClass}">${finalLabel}</th>`;
        });

        tableHtml += '</tr></thead><tbody><tr>';

        // Generate Table Body
        days.forEach(dayKey => {
            const isToday = dayKey === todayStr;
            const tdClass = isToday ? 'today-column' : '';
            tableHtml += `<td class="${tdClass}">`;

            let closestForecastDt = -1;
            if (isToday) {
                const now = new Date();
                let minDiff = Infinity;
                dailyData[dayKey].forEach(f => {
                    const diff = Math.abs(now - new Date(f.dt * 1000));
                    if (diff < minDiff) {
                        minDiff = diff;
                        closestForecastDt = f.dt;
                    }
                });
            }

            dailyData[dayKey].forEach(f => {
                const date = new Date(f.dt * 1000);
                const timeLabel = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
                const weatherIcon = f.weather[0].icon;
                const iconClass = getWeatherIconClass(weatherIcon);
                let timeSlotClass = (f.dt === closestForecastDt) ? 'current-time' : '';
                if (weatherIcon === '01d') {
                    timeSlotClass += ' clear-sky';
                }

                const weatherDesc = f.weather[0].description;

                const tempC = f.main.temp;

                let colorClass = '';
                if (tempC < 30) colorClass = 'temp-good';
                else colorClass = 'temp-danger';

                tableHtml += `
                    <div class="time-slot ${timeSlotClass.trim()}">
                        <div class="time">${timeLabel}</div>
                        <div class="icon"><i class="wi ${iconClass}"></i></div>
                        <div class="desc">${weatherDesc}</div>
                        <div class="temp ${colorClass}">${tempC.toFixed(1)}&deg;C</div>
                    </div>
                `;
            });
            tableHtml += '</td>';
        });

        tableHtml += '</tr></tbody></table></div>';
        weatherResults.innerHTML = tableHtml;
    }

    function getWeatherIconClass(iconCode) {
        const iconMapping = {
            '01d': 'wi-day-sunny',
            '01n': 'wi-night-clear',
            '02d': 'wi-day-cloudy',
            '02n': 'wi-night-cloudy',
            '03d': 'wi-cloud',
            '03n': 'wi-cloud',
            '04d': 'wi-cloudy',
            '04n': 'wi-cloudy',
            '09d': 'wi-showers',
            '09n': 'wi-showers',
            '10d': 'wi-day-rain',
            '10n': 'wi-night-rain',
            '11d': 'wi-thunderstorm',
            '11n': 'wi-thunderstorm',
            '13d': 'wi-snow',
            '13n': 'wi-snow',
            '50d': 'wi-fog',
            '50n': 'wi-fog',
        };
        return iconMapping[iconCode] || 'wi-na';
    }

    // Initialize map on load with defaults
    updateWindyMap();
});
