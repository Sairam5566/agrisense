# Agriculture Mobile App

A comprehensive mobile application for farmers built with Flutter, providing features like disease detection, soil analysis, market price information, weather forecasting, crop recommendations, and government schemes.

## Features

1. **User Authentication**
   - Farmer login/registration
   - Customer login/registration

2. **Disease Detection**
   - Take photos of plants to detect diseases
   - Get detailed analysis and protection tips

3. **Soil Analysis**
   - Analyze soil type from photos
   - Receive fertilizer recommendations

4. **Market Prices**
   - View current crop prices
   - Filter by state

5. **Weather Forecast**
   - Get weather information based on location
   - Helpful for agricultural planning

6. **ML Recommendations**
   - Crop prediction based on location and season
   - Crop recommendations based on soil conditions
   - Fertilizer recommendations based on crop type

7. **Marketplace**
   - List crops for sale
   - View buyer requirements

8. **Government Schemes**
   - Browse agricultural schemes
   - View detailed scheme information

9. **Multi-language Support**
   - English and Hindi interfaces

## Prerequisites

- Flutter SDK (3.0 or higher)
- Android Studio
- Android SDK
- Python FastAPI backend (from the original project)

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd agriculture_mobile_app
   ```

2. **Install dependencies**
   ```bash
   flutter pub get
   ```

3. **Configure backend connection**
   - Update the `baseUrl` in `lib/utils/constants.dart` to point to your FastAPI backend
   - For emulator testing, use `http://10.0.2.2:8000`
   - For physical device testing, use your computer's IP address

4. **Run the app**
   ```bash
   flutter run
   ```

## Building Android APK

1. **Create a release build**
   ```bash
   flutter build apk
   ```

2. **Create a split build (recommended for smaller APK sizes)**
   ```bash
   flutter build apk --split-per-abi
   ```

3. **Find the APK**
   - Release build: `build/app/outputs/flutter-apk/app-release.apk`
   - Split builds: `build/app/outputs/flutter-apk/app-arm64-v8a-release.apk`, `build/app/outputs/flutter-apk/app-armeabi-v7a-release.apk`, etc.

## Backend Configuration

To use all features of the app, ensure your FastAPI backend is running:

1. **Start the backend server**
   ```bash
   python main.py
   ```

2. **API Endpoints Used**
   - Authentication: `/api/auth/login`, `/api/auth/farmer/register`
   - Disease Detection: `/api/disease/predict`
   - Soil Analysis: `/api/soil/analyze`
   - Weather Forecast: `/api/weather/forecast`
   - ML Predictions: `/api/ml/crop-prediction`, `/api/ml/crop-recommendation`, `/api/ml/fertilizer-recommendation`
   - Marketplace: `/api/marketplace/listings`, `/api/marketplace/requirements`
   - Government Schemes: `/api/schemes/`

## Dependencies

The app uses the following Flutter packages:
- `http` for API communication
- `flutter_secure_storage` for secure token storage
- `image_picker` for capturing and selecting images
- `provider` for state management
- `intl` for internationalization
- `geolocator` for location services
- `shared_preferences` for local data storage
- `speech_to_text` for speech recognition
- `flutter_tts` for text-to-speech

## Error Handling

The app includes comprehensive error handling for:
- Network connectivity issues
- API errors
- Image processing errors
- Location permission errors
- Form validation errors

## UI Design Principles

The app follows these design principles for farmer-friendly experience:
- Simple and clean interface
- Large buttons for easy tapping
- Clear typography
- Intuitive navigation
- Visual feedback for user actions
- Error messages in plain language

## Testing

To test the app:
1. Use Android Emulator for initial testing
2. Test on physical Android devices for real-world experience
3. Verify all API endpoints are working correctly
4. Test image upload features with various file types
5. Check multi-language functionality

## Deployment

To deploy the app:
1. Generate signed APK for Google Play Store
2. Follow Google Play Store guidelines for agricultural apps
3. Ensure all permissions are properly explained
4. Test thoroughly before submission

## Support

For issues and feature requests, please create an issue in the repository.
