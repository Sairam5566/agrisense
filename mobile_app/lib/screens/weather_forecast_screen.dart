import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:agriculture_mobile_app/services/api_service.dart';

class WeatherForecastScreen extends StatefulWidget {
  const WeatherForecastScreen({super.key});

  @override
  State<WeatherForecastScreen> createState() => _WeatherForecastScreenState();
}

class _WeatherForecastScreenState extends State<WeatherForecastScreen> {
  final ApiService _apiService = ApiService();
  Map<String, dynamic>? _weatherData;
  bool _isLoading = false;
  bool _locationEnabled = false;
  String _error = '';

  @override
  void initState() {
    super.initState();
    _checkLocationPermission();
  }

  Future<void> _checkLocationPermission() async {
    bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
    setState(() {
      _locationEnabled = serviceEnabled;
    });
    
    if (!serviceEnabled) {
      setState(() {
        _error = 'Location services are disabled. Please enable location to get weather forecast.';
      });
      return;
    }

    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        setState(() {
          _error = 'Location permissions are denied. Please grant location permission to get weather forecast.';
        });
        return;
      }
    }

    if (permission == LocationPermission.deniedForever) {
      setState(() {
        _error = 'Location permissions are permanently denied. Please enable location in settings.';
      });
      return;
    }

    _fetchWeatherData();
  }

  Future<void> _fetchWeatherData() async {
    setState(() {
      _isLoading = true;
      _error = '';
    });

    try {
      Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );
      
      final result = await _apiService.getWeatherForecast(
        position.latitude,
        position.longitude,
      );
      
      setState(() {
        _weatherData = result;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _error = e.toString();
      });
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString())),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      appBar: AppBar(
        backgroundColor: const Color(0xFF4CAF50),
        title: const Text(
          'Weather Forecast',
          style: TextStyle(color: Colors.white),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'Weather Forecast',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Color(0xFF333333),
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              'Get weather information for your location',
              style: TextStyle(
                fontSize: 16,
                color: Color(0xFF757575),
              ),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _locationEnabled ? _fetchWeatherData : _checkLocationPermission,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF4CAF50),
              ),
              child: const Text('Get Current Weather'),
            ),
            const SizedBox(height: 20),
            // Weather data display
            Expanded(
              child: _isLoading
                  ? const Center(
                      child: CircularProgressIndicator(
                        valueColor:
                            AlwaysStoppedAnimation<Color>(Color(0xFF4CAF50)),
                      ),
                    )
                  : _error.isNotEmpty
                      ? Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              const Icon(
                                Icons.error,
                                size: 50,
                                color: Colors.red,
                              ),
                              const SizedBox(height: 10),
                              Text(
                                _error,
                                textAlign: TextAlign.center,
                                style: const TextStyle(
                                  fontSize: 16,
                                  color: Color(0xFF757575),
                                ),
                              ),
                            ],
                          ),
                        )
                      : _weatherData == null
                          ? const Center(
                              child: Text(
                                'No weather data available',
                                style: TextStyle(
                                  fontSize: 16,
                                  color: Color(0xFF757575),
                                ),
                              ),
                            )
                          : _buildWeatherDisplay(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildWeatherDisplay() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(10),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.2),
            blurRadius: 5,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Current Weather',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Color(0xFF333333),
              ),
            ),
            const SizedBox(height: 15),
            if (_weatherData!.containsKey('main'))
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Temperature: ${_weatherData!['main']['temp'] ?? 'N/A'}°C',
                    style: const TextStyle(
                      fontSize: 18,
                      color: Color(0xFF333333),
                    ),
                  ),
                  const SizedBox(height: 10),
                  Text(
                    'Humidity: ${_weatherData!['main']['humidity'] ?? 'N/A'}%',
                    style: const TextStyle(
                      fontSize: 18,
                      color: Color(0xFF333333),
                    ),
                  ),
                  const SizedBox(height: 10),
                  Text(
                    'Pressure: ${_weatherData!['main']['pressure'] ?? 'N/A'} hPa',
                    style: const TextStyle(
                      fontSize: 18,
                      color: Color(0xFF333333),
                    ),
                  ),
                ],
              ),
            const SizedBox(height: 15),
            if (_weatherData!.containsKey('weather') &&
                _weatherData!['weather'].isNotEmpty)
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Condition: ${_weatherData!['weather'][0]['main'] ?? 'N/A'}',
                    style: const TextStyle(
                      fontSize: 18,
                      color: Color(0xFF333333),
                    ),
                  ),
                  const SizedBox(height: 10),
                  Text(
                    'Description: ${_weatherData!['weather'][0]['description'] ?? 'N/A'}',
                    style: const TextStyle(
                      fontSize: 16,
                      color: Color(0xFF757575),
                    ),
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }
}
