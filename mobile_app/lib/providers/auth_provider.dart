import 'package:flutter/material.dart';
import 'package:agriculture_mobile_app/services/api_service.dart';
import 'package:agriculture_mobile_app/models/user.dart';
import 'package:agriculture_mobile_app/utils/constants.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class AuthProvider with ChangeNotifier {
  User? _user;
  bool _isLoading = false;
  String? _token;
  final ApiService _apiService = ApiService();
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  User? get user => _user;
  bool get isLoading => _isLoading;
  String? get token => _token;
  bool get isAuthenticated => _token != null && _user != null;

  AuthProvider() {
    _loadToken();
  }

  Future<void> _loadToken() async {
    _token = await _storage.read(key: 'token');
    if (_token != null) {
      // Load user data from storage or fetch from API
      // For simplicity, we'll just keep the token
    }
    notifyListeners();
  }

  Future<bool> login(String phone, String password, String userType) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await _apiService.login(phone, password, userType);
      if (response.containsKey('access_token')) {
        _token = response['access_token'];
        await _storage.write(key: 'token', value: _token);
        await _storage.write(key: 'userType', value: userType);
        
        // Create user object
        _user = User(
          id: response['user_id'] ?? 0,
          name: '', // Will be fetched separately
          phone: phone,
          email: '',
          userType: userType,
        );
        
        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        _isLoading = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> registerFarmer({
    required String name,
    required String phone,
    required String password,
  }) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await _apiService.registerFarmer(
        name: name,
        phone: phone,
        password: password,
      );
      
      _isLoading = false;
      notifyListeners();
      
      if (response.containsKey('message')) {
        return true;
      } else {
        return false;
      }
    } catch (e) {
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<void> logout() async {
    _token = null;
    _user = null;
    await _storage.delete(key: 'token');
    await _storage.delete(key: 'userType');
    notifyListeners();
  }
}
