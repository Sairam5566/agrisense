import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:agriculture_mobile_app/services/api_service.dart';

class DiseaseDetectionScreen extends StatefulWidget {
  const DiseaseDetectionScreen({super.key});

  @override
  State<DiseaseDetectionScreen> createState() => _DiseaseDetectionScreenState();
}

class _DiseaseDetectionScreenState extends State<DiseaseDetectionScreen> {
  final ApiService _apiService = ApiService();
  File? _selectedImage;
  Map<String, dynamic>? _predictionResult;
  bool _isLoading = false;
  final ImagePicker _picker = ImagePicker();

  Future<void> _pickImage() async {
    final XFile? image = await _picker.pickImage(source: ImageSource.camera);
    if (image != null) {
      setState(() {
        _selectedImage = File(image.path);
        _predictionResult = null;
      });
    }
  }

  Future<void> _pickImageFromGallery() async {
    final XFile? image = await _picker.pickImage(source: ImageSource.gallery);
    if (image != null) {
      setState(() {
        _selectedImage = File(image.path);
        _predictionResult = null;
      });
    }
  }

  Future<void> _predictDisease() async {
    if (_selectedImage == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select an image first')),
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final result = await _apiService.predictDisease(_selectedImage!);
      setState(() {
        _predictionResult = result;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
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
          'Disease Detection',
          style: TextStyle(color: Colors.white),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'Plant Disease Detection',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Color(0xFF333333),
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              'Take a photo of the plant to detect diseases',
              style: TextStyle(
                fontSize: 16,
                color: Color(0xFF757575),
              ),
            ),
            const SizedBox(height: 20),
            // Image picker section
            Container(
              height: 200,
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
              child: _selectedImage == null
                  ? Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(
                          Icons.add_a_photo,
                          size: 50,
                          color: Color(0xFF4CAF50),
                        ),
                        const SizedBox(height: 10),
                        const Text(
                          'No image selected',
                          style: TextStyle(
                            fontSize: 16,
                            color: Color(0xFF757575),
                          ),
                        ),
                        const SizedBox(height: 20),
                        ElevatedButton(
                          onPressed: _pickImage,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF4CAF50),
                          ),
                          child: const Text('Take Photo'),
                        ),
                      ],
                    )
                  : Stack(
                      children: [
                        Image.file(
                          _selectedImage!,
                          fit: BoxFit.cover,
                          width: double.infinity,
                          height: double.infinity,
                        ),
                        Positioned(
                          top: 10,
                          right: 10,
                          child: CircleAvatar(
                            backgroundColor: Colors.white,
                            child: IconButton(
                              icon: const Icon(Icons.close, color: Colors.red),
                              onPressed: () {
                                setState(() {
                                  _selectedImage = null;
                                  _predictionResult = null;
                                });
                              },
                            ),
                          ),
                        ),
                      ],
                    ),
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton(
                    onPressed: _pickImageFromGallery,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.white,
                      foregroundColor: const Color(0xFF4CAF50),
                      side: const BorderSide(color: Color(0xFF4CAF50)),
                    ),
                    child: const Text('Choose from Gallery'),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: ElevatedButton(
                    onPressed: _predictDisease,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF4CAF50),
                    ),
                    child: const Text('Detect Disease'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            // Results section
            if (_isLoading)
              const Center(
                child: CircularProgressIndicator(
                  valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF4CAF50)),
                ),
              )
            else if (_predictionResult != null)
              Container(
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
                        'Detection Results',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF333333),
                        ),
                      ),
                      const SizedBox(height: 15),
                      Text(
                        'Plant: ${_predictionResult!['plant'] ?? 'Unknown'}',
                        style: const TextStyle(
                          fontSize: 18,
                          color: Color(0xFF333333),
                        ),
                      ),
                      const SizedBox(height: 10),
                      Text(
                        'Disease: ${_predictionResult!['disease'] ?? 'Unknown'}',
                        style: TextStyle(
                          fontSize: 18,
                          color: _predictionResult!['disease'] == 'Healthy Plant'
                              ? Colors.green
                              : Colors.red,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      if (_predictionResult!.containsKey('confidence'))
                        Padding(
                          padding: const EdgeInsets.only(top: 10),
                          child: Text(
                            'Confidence: ${_predictionResult!['confidence']}',
                            style: const TextStyle(
                              fontSize: 16,
                              color: Color(0xFF757575),
                            ),
                          ),
                        ),
                      if (_predictionResult!.containsKey('description'))
                        Padding(
                          padding: const EdgeInsets.only(top: 15),
                          child: Text(
                            'Description:\n${_predictionResult!['description']}',
                            style: const TextStyle(
                              fontSize: 16,
                              color: Color(0xFF333333),
                            ),
                          ),
                        ),
                      if (_predictionResult!.containsKey('causes'))
                        Padding(
                          padding: const EdgeInsets.only(top: 15),
                          child: Text(
                            'Causes:\n${_predictionResult!['causes']}',
                            style: const TextStyle(
                              fontSize: 16,
                              color: Color(0xFF333333),
                            ),
                          ),
                        ),
                      if (_predictionResult!.containsKey('protection'))
                        Padding(
                          padding: const EdgeInsets.only(top: 15),
                          child: Text(
                            'Protection:\n${_predictionResult!['protection']}',
                            style: const TextStyle(
                              fontSize: 16,
                              color: Color(0xFF333333),
                            ),
                          ),
                        ),
                      if (_predictionResult!.containsKey('fertilizer'))
                        Padding(
                          padding: const EdgeInsets.only(top: 15),
                          child: Text(
                            'Fertilizer Tips:\n${_predictionResult!['fertilizer']}',
                            style: const TextStyle(
                              fontSize: 16,
                              color: Color(0xFF333333),
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
