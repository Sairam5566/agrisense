import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:agriculture_mobile_app/utils/constants.dart';

class ApiService {
  final String _baseUrl = Constants.baseUrl;

  // Login API call
  Future<Map<String, dynamic>> login(
      String phone, String password, String userType) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl${Constants.loginEndpoint}'),
        body: {
          'phone_no': phone,
          'password': password,
          'user_type': userType,
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to login: ${response.body}');
      }
    } on SocketException {
      throw Exception(Constants.networkError);
    } on HttpException {
      throw Exception(Constants.networkError);
    } catch (e) {
      throw Exception(Constants.serverError);
    }
  }

  // Farmer Registration API call
  Future<Map<String, dynamic>> registerFarmer({
    required String name,
    required String phone,
    required String password,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl${Constants.registerFarmerEndpoint}'),
        body: {
          'name': name,
          'phone_no': phone,
          'password': password,
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to register farmer: ${response.body}');
      }
    } on SocketException {
      throw Exception(Constants.networkError);
    } on HttpException {
      throw Exception(Constants.networkError);
    } catch (e) {
      throw Exception(Constants.serverError);
    }
  }

  // Disease Prediction API call
  Future<Map<String, dynamic>> predictDisease(File imageFile) async {
    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('$_baseUrl${Constants.diseasePredictEndpoint}'),
      );

      var multipartFile = await http.MultipartFile.fromPath(
        'image',
        imageFile.path,
      );

      request.files.add(multipartFile);

      final response = await request.send();
      final respStr = await response.stream.bytesToString();

      if (response.statusCode == 200) {
        return json.decode(respStr);
      } else {
        throw Exception('Failed to predict disease: $respStr');
      }
    } on SocketException {
      throw Exception(Constants.networkError);
    } on HttpException {
      throw Exception(Constants.networkError);
    } catch (e) {
      throw Exception(Constants.serverError);
    }
  }

  // Soil Analysis API call
  Future<Map<String, dynamic>> analyzeSoil(File imageFile) async {
    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('$_baseUrl${Constants.soilAnalysisEndpoint}'),
      );

      var multipartFile = await http.MultipartFile.fromPath(
        'file',
        imageFile.path,
      );

      request.files.add(multipartFile);

      final response = await request.send();
      final respStr = await response.stream.bytesToString();

      if (response.statusCode == 200) {
        return json.decode(respStr);
      } else {
        throw Exception('Failed to analyze soil: $respStr');
      }
    } on SocketException {
      throw Exception(Constants.networkError);
    } on HttpException {
      throw Exception(Constants.networkError);
    } catch (e) {
      throw Exception(Constants.serverError);
    }
  }

  // Weather Forecast API call
  Future<Map<String, dynamic>> getWeatherForecast(
      double lat, double lon) async {
    try {
      final response = await http.get(
        Uri.parse(
            '$_baseUrl${Constants.weatherForecastEndpoint}?lat=$lat&lon=$lon'),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to get weather forecast: ${response.body}');
      }
    } on SocketException {
      throw Exception(Constants.networkError);
    } on HttpException {
      throw Exception(Constants.networkError);
    } catch (e) {
      throw Exception(Constants.serverError);
    }
  }

  // Crop Prediction API call
  Future<Map<String, dynamic>> predictCrop(
      String state, String district, String season) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl${Constants.cropPredictionEndpoint}'),
        body: {
          'state': state,
          'district': district,
          'season': season,
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to predict crop: ${response.body}');
      }
    } on SocketException {
      throw Exception(Constants.networkError);
    } on HttpException {
      throw Exception(Constants.networkError);
    } catch (e) {
      throw Exception(Constants.serverError);
    }
  }

  // Crop Recommendation API call
  Future<Map<String, dynamic>> recommendCrop({
    required double nitrogen,
    required double phosphorus,
    required double potassium,
    required double temperature,
    required double humidity,
    required double ph,
    required double rainfall,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl${Constants.cropRecommendationEndpoint}'),
        body: {
          'nitrogen': nitrogen.toString(),
          'phosphorus': phosphorus.toString(),
          'potassium': potassium.toString(),
          'temperature': temperature.toString(),
          'humidity': humidity.toString(),
          'ph': ph.toString(),
          'rainfall': rainfall.toString(),
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to recommend crop: ${response.body}');
      }
    } on SocketException {
      throw Exception(Constants.networkError);
    } on HttpException {
      throw Exception(Constants.networkError);
    } catch (e) {
      throw Exception(Constants.serverError);
    }
  }

  // Fertilizer Recommendation API call
  Future<Map<String, dynamic>> recommendFertilizer({
    required String crop,
    required String soilType,
    required double nitrogen,
    required double phosphorus,
    required double potassium,
    required double temperature,
    required double humidity,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl${Constants.fertilizerRecommendationEndpoint}'),
        body: {
          'crop': crop,
          'soil_type': soilType,
          'nitrogen': nitrogen.toString(),
          'phosphorus': phosphorus.toString(),
          'potassium': potassium.toString(),
          'temperature': temperature.toString(),
          'humidity': humidity.toString(),
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to recommend fertilizer: ${response.body}');
      }
    } on SocketException {
      throw Exception(Constants.networkError);
    } on HttpException {
      throw Exception(Constants.networkError);
    } catch (e) {
      throw Exception(Constants.serverError);
    }
  }

  // Get Marketplace Listings
  Future<Map<String, dynamic>> getMarketplaceListings() async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl${Constants.marketplaceListingsEndpoint}'),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to get listings: ${response.body}');
      }
    } on SocketException {
      throw Exception(Constants.networkError);
    } on HttpException {
      throw Exception(Constants.networkError);
    } catch (e) {
      throw Exception(Constants.serverError);
    }
  }

  // Create Marketplace Listing
  Future<Map<String, dynamic>> createMarketplaceListing({
    required int farmerId,
    required String cropName,
    required double quantity,
    required double pricePerUnit,
    String unit = 'kg',
    String? description,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl${Constants.marketplaceListingsEndpoint}'),
        body: {
          'farmer_id': farmerId.toString(),
          'crop_name': cropName,
          'quantity': quantity.toString(),
          'unit': unit,
          'price_per_unit': pricePerUnit.toString(),
          'description': description ?? '',
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to create listing: ${response.body}');
      }
    } on SocketException {
      throw Exception(Constants.networkError);
    } on HttpException {
      throw Exception(Constants.networkError);
    } catch (e) {
      throw Exception(Constants.serverError);
    }
  }

  // Get Buyer Requirements
  Future<Map<String, dynamic>> getBuyerRequirements() async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl${Constants.marketplaceRequirementsEndpoint}'),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to get requirements: ${response.body}');
      }
    } on SocketException {
      throw Exception(Constants.networkError);
    } on HttpException {
      throw Exception(Constants.networkError);
    } catch (e) {
      throw Exception(Constants.serverError);
    }
  }

  // Create Buyer Requirement
  Future<Map<String, dynamic>> createBuyerRequirement({
    required String requirement,
    int? buyerId,
    String? contactName,
    String? contactPhone,
    String? contactEmail,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl${Constants.marketplaceRequirementsEndpoint}'),
        body: {
          'requirement': requirement,
          if (buyerId != null) 'buyer_id': buyerId.toString(),
          if (contactName != null) 'contact_name': contactName,
          if (contactPhone != null) 'contact_phone': contactPhone,
          if (contactEmail != null) 'contact_email': contactEmail,
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to create requirement: ${response.body}');
      }
    } on SocketException {
      throw Exception(Constants.networkError);
    } on HttpException {
      throw Exception(Constants.networkError);
    } catch (e) {
      throw Exception(Constants.serverError);
    }
  }

  // Get Government Schemes
  Future<Map<String, dynamic>> getGovernmentSchemes() async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl${Constants.schemesEndpoint}'),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to get schemes: ${response.body}');
      }
    } on SocketException {
      throw Exception(Constants.networkError);
    } on HttpException {
      throw Exception(Constants.networkError);
    } catch (e) {
      throw Exception(Constants.serverError);
    }
  }
}
