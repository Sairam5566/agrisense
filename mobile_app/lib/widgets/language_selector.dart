import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:agriculture_mobile_app/providers/language_provider.dart';

class LanguageSelector extends StatelessWidget {
  const LanguageSelector({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<LanguageProvider>(
      builder: (context, languageProvider, child) {
        return Padding(
          padding: const EdgeInsets.all(10),
          child: DropdownButton<String>(
            value: languageProvider.currentLanguage,
            icon: const Icon(Icons.language),
            items: const [
              DropdownMenuItem(
                value: 'en',
                child: Text('English'),
              ),
              DropdownMenuItem(
                value: 'hi',
                child: Text('हिंदी'),
              ),
            ],
            onChanged: (String? newLanguage) {
              if (newLanguage != null) {
                languageProvider.setLanguage(newLanguage);
              }
            },
          ),
        );
      },
    );
  }
}
