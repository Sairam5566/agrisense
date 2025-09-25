import 'package:flutter/material.dart';
import 'package:agriculture_mobile_app/providers/auth_provider.dart';
import 'package:agriculture_mobile_app/widgets/feature_card.dart';
import 'package:agriculture_mobile_app/screens/disease_detection_screen.dart';
import 'package:agriculture_mobile_app/screens/soil_analysis_screen.dart';
import 'package:agriculture_mobile_app/screens/market_prices_screen.dart';
import 'package:agriculture_mobile_app/screens/weather_forecast_screen.dart';
import 'package:agriculture_mobile_app/screens/ml_recommendations_screen.dart';
import 'package:agriculture_mobile_app/screens/marketplace_screen.dart';
import 'package:agriculture_mobile_app/screens/government_schemes_screen.dart';
import 'package:agriculture_mobile_app/widgets/language_selector.dart';
import 'package:provider/provider.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);
    
    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      appBar: AppBar(
        backgroundColor: const Color(0xFF4CAF50),
        title: const Text(
          'Agriculture Portal',
          style: TextStyle(color: Colors.white),
        ),
        actions: [
          const LanguageSelector(),
          IconButton(
            icon: const Icon(Icons.logout, color: Colors.white),
            onPressed: () {
              authProvider.logout();
              Navigator.pushReplacementNamed(context, '/login');
            },
          ),
        ],
      },
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'Welcome to Agriculture Portal',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Color(0xFF333333),
              ),
            ),
            const SizedBox(height: 5),
            Text(
              'Empowering farmers with technology',
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey[600],
              ),
            ),
            const SizedBox(height: 20),
            Expanded(
              child: GridView.count(
                crossAxisCount: 2,
                crossAxisSpacing: 15,
                mainAxisSpacing: 15,
                children: [
                  FeatureCard(
                    title: 'Disease Detection',
                    icon: Icons.local_hospital,
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => const DiseaseDetectionScreen(),
                        ),
                      );
                    },
                  ),
                  FeatureCard(
                    title: 'Soil Analysis',
                    icon: Icons.eco,
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => const SoilAnalysisScreen(),
                        ),
                      );
                    },
                  ),
                  FeatureCard(
                    title: 'Market Prices',
                    icon: Icons.shopping_cart,
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => const MarketPricesScreen(),
                        ),
                      );
                    },
                  ),
                  FeatureCard(
                    title: 'Weather Forecast',
                    icon: Icons.wb_sunny,
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => const WeatherForecastScreen(),
                        ),
                      );
                    },
                  ),
                  FeatureCard(
                    title: 'Crop Recommendations',
                    icon: Icons.agriculture,
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => const MLRecommendationsScreen(),
                        ),
                      );
                    },
                  ),
                  FeatureCard(
                    title: 'Marketplace',
                    icon: Icons.store,
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => const MarketplaceScreen(),
                        ),
                      );
                    },
                  ),
                  FeatureCard(
                    title: 'Government Schemes',
                    icon: Icons.policy,
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => const GovernmentSchemesScreen(),
                        ),
                      );
                    },
                  ),
                  FeatureCard(
                    title: 'About Farming',
                    icon: Icons.info,
                    color: const Color(0xFF2196F3),
                    onTap: () {
                      // TODO: Implement About Farming screen
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Feature coming soon!')),
                      );
                    },
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
