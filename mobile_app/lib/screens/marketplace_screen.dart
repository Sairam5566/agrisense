import 'package:flutter/material.dart';
import 'package:agriculture_mobile_app/services/api_service.dart';

class MarketplaceScreen extends StatefulWidget {
  const MarketplaceScreen({super.key});

  @override
  State<MarketplaceScreen> createState() => _MarketplaceScreenState();
}

class _MarketplaceScreenState extends State<MarketplaceScreen>
    with TickerProviderStateMixin {
  final ApiService _apiService = ApiService();
  List<dynamic> _listings = [];
  List<dynamic> _requirements = [];
  bool _isLoading = false;
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _fetchData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _fetchData() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final listingsResult = await _apiService.getMarketplaceListings();
      final requirementsResult = await _apiService.getBuyerRequirements();
      
      setState(() {
        _listings = listingsResult['items'] ?? [];
        _requirements = requirementsResult['items'] ?? [];
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
          'Marketplace',
          style: TextStyle(color: Colors.white),
        ),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Sell Crops'),
            Tab(text: 'Buy Requirements'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          // Farmer Listings Tab
          _buildListingsTab(),
          // Buyer Requirements Tab
          _buildRequirementsTab(),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        backgroundColor: const Color(0xFF4CAF50),
        child: const Icon(Icons.add, color: Colors.white),
        onPressed: () {
          _showCreateListingDialog();
        },
      ),
    );
  }

  Widget _buildListingsTab() {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text(
            'Sell Your Crops',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Color(0xFF333333),
            ),
          ),
          const SizedBox(height: 10),
          const Text(
            'List your crops for sale in the marketplace',
            style: TextStyle(
              fontSize: 16,
              color: Color(0xFF757575),
            ),
          ),
          const SizedBox(height: 20),
          ElevatedButton(
            onPressed: _fetchData,
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF4CAF50),
            ),
            child: const Text('Refresh Listings'),
          ),
          const SizedBox(height: 20),
          Expanded(
            child: _isLoading
                ? const Center(
                    child: CircularProgressIndicator(
                      valueColor:
                          AlwaysStoppedAnimation<Color>(Color(0xFF4CAF50)),
                    ),
                  )
                : _listings.isEmpty
                    ? const Center(
                        child: Text(
                          'No listings available',
                          style: TextStyle(
                            fontSize: 16,
                            color: Color(0xFF757575),
                          ),
                        ),
                      )
                    : ListView.builder(
                        itemCount: _listings.length,
                        itemBuilder: (context, index) {
                          final listing = _listings[index];
                          return Card(
                            elevation: 3,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(10),
                            ),
                            child: Padding(
                              padding: const EdgeInsets.all(15),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    mainAxisAlignment:
                                        MainAxisAlignment.spaceBetween,
                                    children: [
                                      Text(
                                        listing['crop_name'] ?? 'Unknown Crop',
                                        style: const TextStyle(
                                          fontSize: 18,
                                          fontWeight: FontWeight.bold,
                                          color: Color(0xFF333333),
                                        ),
                                      ),
                                      Text(
                                        '₹${listing['price_per_unit'] ?? 'N/A'}/${listing['unit'] ?? 'kg'}',
                                        style: const TextStyle(
                                          fontSize: 18,
                                          color: Color(0xFF4CAF50),
                                          fontWeight: FontWeight.w500,
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 10),
                                  Text(
                                    'Quantity: ${listing['quantity'] ?? 'N/A'} ${listing['unit'] ?? 'kg'}',
                                    style: const TextStyle(
                                      fontSize: 16,
                                      color: Color(0xFF333333),
                                    ),
                                  ),
                                  const SizedBox(height: 5),
                                  Text(
                                    'Posted on: ${listing['created_at'] ?? 'N/A'}',
                                    style: const TextStyle(
                                      fontSize: 14,
                                      color: Color(0xFF757575),
                                    ),
                                  ),
                                  if (listing['description'] != null &&
                                      listing['description'].toString().isNotEmpty)
                                    Padding(
                                      padding: const EdgeInsets.only(top: 10),
                                      child: Text(
                                        listing['description'],
                                        style: const TextStyle(
                                          fontSize: 14,
                                          color: Color(0xFF333333),
                                        ),
                                      ),
                                    ),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
          ),
        ],
      ),
    );
  }

  Widget _buildRequirementsTab() {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text(
            'Buyer Requirements',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Color(0xFF333333),
            ),
          ),
          const SizedBox(height: 10),
          const Text(
            'Check what buyers are looking for',
            style: TextStyle(
              fontSize: 16,
              color: Color(0xFF757575),
            ),
          ),
          const SizedBox(height: 20),
          ElevatedButton(
            onPressed: _fetchData,
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF4CAF50),
            ),
            child: const Text('Refresh Requirements'),
          ),
          const SizedBox(height: 20),
          Expanded(
            child: _isLoading
                ? const Center(
                    child: CircularProgressIndicator(
                      valueColor:
                          AlwaysStoppedAnimation<Color>(Color(0xFF4CAF50)),
                    ),
                  )
                : _requirements.isEmpty
                    ? const Center(
                        child: Text(
                          'No requirements available',
                          style: TextStyle(
                            fontSize: 16,
                            color: Color(0xFF757575),
                          ),
                        ),
                      )
                    : ListView.builder(
                        itemCount: _requirements.length,
                        itemBuilder: (context, index) {
                          final requirement = _requirements[index];
                          return Card(
                            elevation: 3,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(10),
                            ),
                            child: Padding(
                              padding: const EdgeInsets.all(15),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    requirement['requirement'] ??
                                        'No requirement specified',
                                    style: const TextStyle(
                                      fontSize: 16,
                                      color: Color(0xFF333333),
                                    ),
                                  ),
                                  const SizedBox(height: 10),
                                  Text(
                                    'Posted on: ${requirement['created_at'] ?? 'N/A'}',
                                    style: const TextStyle(
                                      fontSize: 14,
                                      color: Color(0xFF757575),
                                    ),
                                  ),
                                  if (requirement['contact_name'] != null)
                                    Padding(
                                      padding: const EdgeInsets.only(top: 5),
                                      child: Text(
                                        'Contact: ${requirement['contact_name']}',
                                        style: const TextStyle(
                                          fontSize: 14,
                                          color: Color(0xFF333333),
                                        ),
                                      ),
                                    ),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
          ),
        ],
      ),
    );
  }

  void _showCreateListingDialog() {
    final _formKey = GlobalKey<FormState>();
    final _cropNameController = TextEditingController();
    final _quantityController = TextEditingController();
    final _priceController = TextEditingController();
    final _descriptionController = TextEditingController();
    String _unit = 'kg';

    final List<String> _units = ['kg', 'ton', 'quintal'];

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Create Listing'),
          content: Form(
            key: _formKey,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextFormField(
                  controller: _cropNameController,
                  decoration: const InputDecoration(
                    labelText: 'Crop Name',
                  ),
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Please enter crop name';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 10),
                TextFormField(
                  controller: _quantityController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(
                    labelText: 'Quantity',
                  ),
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Please enter quantity';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 10),
                DropdownButtonFormField<String>(
                  value: _unit,
                  items: _units.map((String unit) {
                    return DropdownMenuItem<String>(
                      value: unit,
                      child: Text(unit),
                    );
                  }).toList(),
                  onChanged: (String? newUnit) {
                    _unit = newUnit!;
                  },
                  decoration: const InputDecoration(
                    labelText: 'Unit',
                  ),
                ),
                const SizedBox(height: 10),
                TextFormField(
                  controller: _priceController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(
                    labelText: 'Price per unit',
                  ),
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Please enter price';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 10),
                TextFormField(
                  controller: _descriptionController,
                  decoration: const InputDecoration(
                    labelText: 'Description (Optional)',
                  ),
                  maxLines: 3,
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
              },
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () {
                if (_formKey.currentState!.validate()) {
                  _createListing(
                    cropName: _cropNameController.text,
                    quantity: double.tryParse(_quantityController.text) ?? 0,
                    price: double.tryParse(_priceController.text) ?? 0,
                    description: _descriptionController.text,
                    unit: _unit,
                  );
                  Navigator.of(context).pop();
                }
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF4CAF50),
              ),
              child: const Text('Create'),
            ),
          ],
        );
      },
    );
  }

  Future<void> _createListing({
    required String cropName,
    required double quantity,
    required double price,
    required String description,
    required String unit,
  }) async {
    try {
      final result = await _apiService.createMarketplaceListing(
        farmerId: 1, // This should come from the authenticated user
        cropName: cropName,
        quantity: quantity,
        pricePerUnit: price,
        description: description,
        unit: unit,
      );
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(result['message'] ?? 'Listing created successfully'),
          backgroundColor: const Color(0xFF4CAF50),
        ),
      );
      
      // Refresh data
      _fetchData();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString())),
      );
    }
  }
}
