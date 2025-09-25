class User {
  final int id;
  final String name;
  final String phone;
  final String email;
  final String userType;

  User({
    required this.id,
    required this.name,
    required this.phone,
    required this.email,
    required this.userType,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['user_id'] ?? 0,
      name: json['name'] ?? '',
      phone: json['phone'] ?? '',
      email: json['email'] ?? '',
      userType: json['user_type'] ?? 'farmer',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'user_id': id,
      'name': name,
      'phone': phone,
      'email': email,
      'user_type': userType,
    };
  }
}
