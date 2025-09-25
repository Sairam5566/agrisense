class Constants {
  // API Configuration
  static const String baseUrl = 'http://10.0.2.2:8000'; // Android emulator localhost
  // For physical device testing, replace with your actual backend IP address
  // static const String baseUrl = 'http://YOUR_SERVER_IP:8000';
  
  // API Endpoints
  static const String loginEndpoint = '/api/auth/login';
  static const String registerFarmerEndpoint = '/api/auth/farmer/register';
  static const String registerCustomerEndpoint = '/api/auth/customer/register';
  static const String diseasePredictEndpoint = '/api/disease/predict';
  static const String soilAnalysisEndpoint = '/api/soil/analyze';
  static const String weatherForecastEndpoint = '/api/weather/forecast';
  static const String cropPredictionEndpoint = '/api/ml/crop-prediction';
  static const String cropRecommendationEndpoint = '/api/ml/crop-recommendation';
  static const String fertilizerRecommendationEndpoint = '/api/ml/fertilizer-recommendation';
  static const String marketplaceListingsEndpoint = '/api/marketplace/listings';
  static const String marketplaceRequirementsEndpoint = '/api/marketplace/requirements';
  static const String schemesEndpoint = '/api/schemes/';
  
  // User Types
  static const String farmerUserType = 'farmer';
  static const String customerUserType = 'customer';
  static const String adminUserType = 'admin';
  
  // Storage Keys
  static const String tokenKey = 'token';
  static const String userTypeKey = 'userType';
  
  // App Colors
  static const Color primaryColor = Color(0xFF4CAF50);
  static const Color secondaryColor = Color(0xFF8BC34A);
  static const Color accentColor = Color(0xFFC8E6C9);
  static const Color backgroundColor = Color(0xFFF5F5F5);
  static const Color textColor = Color(0xFF333333);
  static const Color lightTextColor = Color(0xFF757575);
  
  // Error Messages
  static const String networkError = 'Network error. Please check your connection.';
  static const String serverError = 'Server error. Please try again later.';
  static const String invalidCredentials = 'Invalid credentials. Please try again.';
}
