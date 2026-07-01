"""Curated list of real Indian-market maker/model entries used to seed the database.

Each entry's `segment` (entry/economy/mid/premium/luxury/ev) is a generation-time hint
consumed by `app.seed.generators` to pick realistic price bands, specs, and feature
richness. It is not persisted to the database.
"""

MAKERS_AND_MODELS = [
    # Maruti Suzuki (India)
    {"maker": "Maruti Suzuki", "country": "India", "model": "Alto K10", "body_type": "hatchback", "segment": "entry"},
    {"maker": "Maruti Suzuki", "country": "India", "model": "S-Presso", "body_type": "hatchback", "segment": "entry"},
    {"maker": "Maruti Suzuki", "country": "India", "model": "WagonR", "body_type": "hatchback", "segment": "entry"},
    {"maker": "Maruti Suzuki", "country": "India", "model": "Celerio", "body_type": "hatchback", "segment": "entry"},
    {"maker": "Maruti Suzuki", "country": "India", "model": "Eeco", "body_type": "muv", "segment": "entry"},
    {"maker": "Maruti Suzuki", "country": "India", "model": "Ignis", "body_type": "hatchback", "segment": "economy"},
    {"maker": "Maruti Suzuki", "country": "India", "model": "Swift", "body_type": "hatchback", "segment": "economy"},
    {"maker": "Maruti Suzuki", "country": "India", "model": "Baleno", "body_type": "hatchback", "segment": "economy"},
    {"maker": "Maruti Suzuki", "country": "India", "model": "Dzire", "body_type": "sedan", "segment": "economy"},
    {"maker": "Maruti Suzuki", "country": "India", "model": "Ciaz", "body_type": "sedan", "segment": "mid"},
    {"maker": "Maruti Suzuki", "country": "India", "model": "Brezza", "body_type": "suv", "segment": "mid"},
    {"maker": "Maruti Suzuki", "country": "India", "model": "Grand Vitara", "body_type": "suv", "segment": "mid"},
    {"maker": "Maruti Suzuki", "country": "India", "model": "Fronx", "body_type": "suv", "segment": "economy"},
    {"maker": "Maruti Suzuki", "country": "India", "model": "Ertiga", "body_type": "muv", "segment": "mid"},
    {"maker": "Maruti Suzuki", "country": "India", "model": "XL6", "body_type": "muv", "segment": "mid"},
    {"maker": "Maruti Suzuki", "country": "India", "model": "Invicto", "body_type": "muv", "segment": "premium"},
    {"maker": "Maruti Suzuki", "country": "India", "model": "Jimny", "body_type": "suv", "segment": "premium"},
    # Hyundai (South Korea)
    {"maker": "Hyundai", "country": "South Korea", "model": "Grand i10 Nios", "body_type": "hatchback", "segment": "entry"},
    {"maker": "Hyundai", "country": "South Korea", "model": "i20", "body_type": "hatchback", "segment": "economy"},
    {"maker": "Hyundai", "country": "South Korea", "model": "Aura", "body_type": "sedan", "segment": "economy"},
    {"maker": "Hyundai", "country": "South Korea", "model": "Verna", "body_type": "sedan", "segment": "mid"},
    {"maker": "Hyundai", "country": "South Korea", "model": "Venue", "body_type": "suv", "segment": "economy"},
    {"maker": "Hyundai", "country": "South Korea", "model": "Exter", "body_type": "suv", "segment": "economy"},
    {"maker": "Hyundai", "country": "South Korea", "model": "Creta", "body_type": "suv", "segment": "mid"},
    {"maker": "Hyundai", "country": "South Korea", "model": "Alcazar", "body_type": "suv", "segment": "mid"},
    {"maker": "Hyundai", "country": "South Korea", "model": "Tucson", "body_type": "suv", "segment": "premium"},
    {"maker": "Hyundai", "country": "South Korea", "model": "Ioniq 5", "body_type": "suv", "segment": "ev"},
    # Tata Motors (India)
    {"maker": "Tata Motors", "country": "India", "model": "Tiago", "body_type": "hatchback", "segment": "entry"},
    {"maker": "Tata Motors", "country": "India", "model": "Tiago EV", "body_type": "hatchback", "segment": "ev"},
    {"maker": "Tata Motors", "country": "India", "model": "Tigor", "body_type": "sedan", "segment": "economy"},
    {"maker": "Tata Motors", "country": "India", "model": "Altroz", "body_type": "hatchback", "segment": "economy"},
    {"maker": "Tata Motors", "country": "India", "model": "Punch", "body_type": "suv", "segment": "economy"},
    {"maker": "Tata Motors", "country": "India", "model": "Nexon", "body_type": "suv", "segment": "mid"},
    {"maker": "Tata Motors", "country": "India", "model": "Nexon EV", "body_type": "suv", "segment": "ev"},
    {"maker": "Tata Motors", "country": "India", "model": "Curvv", "body_type": "suv", "segment": "mid"},
    {"maker": "Tata Motors", "country": "India", "model": "Curvv EV", "body_type": "suv", "segment": "ev"},
    {"maker": "Tata Motors", "country": "India", "model": "Harrier", "body_type": "suv", "segment": "premium"},
    {"maker": "Tata Motors", "country": "India", "model": "Safari", "body_type": "suv", "segment": "premium"},
    # Mahindra (India)
    {"maker": "Mahindra", "country": "India", "model": "Bolero", "body_type": "suv", "segment": "economy"},
    {"maker": "Mahindra", "country": "India", "model": "Bolero Neo", "body_type": "suv", "segment": "economy"},
    {"maker": "Mahindra", "country": "India", "model": "XUV 3XO", "body_type": "suv", "segment": "mid"},
    {"maker": "Mahindra", "country": "India", "model": "Scorpio Classic", "body_type": "suv", "segment": "mid"},
    {"maker": "Mahindra", "country": "India", "model": "Scorpio-N", "body_type": "suv", "segment": "mid"},
    {"maker": "Mahindra", "country": "India", "model": "Thar", "body_type": "suv", "segment": "mid"},
    {"maker": "Mahindra", "country": "India", "model": "Marazzo", "body_type": "muv", "segment": "mid"},
    {"maker": "Mahindra", "country": "India", "model": "XUV700", "body_type": "suv", "segment": "premium"},
    {"maker": "Mahindra", "country": "India", "model": "XUV400 EV", "body_type": "suv", "segment": "ev"},
    # Honda (Japan)
    {"maker": "Honda", "country": "Japan", "model": "Amaze", "body_type": "sedan", "segment": "economy"},
    {"maker": "Honda", "country": "Japan", "model": "City", "body_type": "sedan", "segment": "mid"},
    {"maker": "Honda", "country": "Japan", "model": "City Hybrid", "body_type": "sedan", "segment": "premium"},
    {"maker": "Honda", "country": "Japan", "model": "Elevate", "body_type": "suv", "segment": "mid"},
    {"maker": "Honda", "country": "Japan", "model": "WR-V", "body_type": "suv", "segment": "economy"},
    # Toyota (Japan)
    {"maker": "Toyota", "country": "Japan", "model": "Glanza", "body_type": "hatchback", "segment": "economy"},
    {"maker": "Toyota", "country": "Japan", "model": "Urban Cruiser Taisor", "body_type": "suv", "segment": "economy"},
    {"maker": "Toyota", "country": "Japan", "model": "Rumion", "body_type": "muv", "segment": "economy"},
    {"maker": "Toyota", "country": "Japan", "model": "Innova Crysta", "body_type": "muv", "segment": "mid"},
    {"maker": "Toyota", "country": "Japan", "model": "Innova Hycross", "body_type": "muv", "segment": "premium"},
    {"maker": "Toyota", "country": "Japan", "model": "Fortuner", "body_type": "suv", "segment": "premium"},
    {"maker": "Toyota", "country": "Japan", "model": "Hilux", "body_type": "pickup", "segment": "premium"},
    {"maker": "Toyota", "country": "Japan", "model": "Camry Hybrid", "body_type": "sedan", "segment": "luxury"},
    {"maker": "Toyota", "country": "Japan", "model": "Vellfire", "body_type": "muv", "segment": "luxury"},
    {"maker": "Toyota", "country": "Japan", "model": "Land Cruiser", "body_type": "suv", "segment": "luxury"},
    # Kia (South Korea)
    {"maker": "Kia", "country": "South Korea", "model": "Sonet", "body_type": "suv", "segment": "economy"},
    {"maker": "Kia", "country": "South Korea", "model": "Seltos", "body_type": "suv", "segment": "mid"},
    {"maker": "Kia", "country": "South Korea", "model": "Syros", "body_type": "suv", "segment": "mid"},
    {"maker": "Kia", "country": "South Korea", "model": "Carens", "body_type": "muv", "segment": "mid"},
    {"maker": "Kia", "country": "South Korea", "model": "Carnival", "body_type": "muv", "segment": "premium"},
    {"maker": "Kia", "country": "South Korea", "model": "EV6", "body_type": "suv", "segment": "ev"},
    # Skoda (Czech Republic)
    {"maker": "Skoda", "country": "Czech Republic", "model": "Kylaq", "body_type": "suv", "segment": "economy"},
    {"maker": "Skoda", "country": "Czech Republic", "model": "Slavia", "body_type": "sedan", "segment": "mid"},
    {"maker": "Skoda", "country": "Czech Republic", "model": "Kushaq", "body_type": "suv", "segment": "mid"},
    {"maker": "Skoda", "country": "Czech Republic", "model": "Kodiaq", "body_type": "suv", "segment": "premium"},
    {"maker": "Skoda", "country": "Czech Republic", "model": "Superb", "body_type": "sedan", "segment": "premium"},
    # Volkswagen (Germany)
    {"maker": "Volkswagen", "country": "Germany", "model": "Virtus", "body_type": "sedan", "segment": "mid"},
    {"maker": "Volkswagen", "country": "Germany", "model": "Taigun", "body_type": "suv", "segment": "mid"},
    {"maker": "Volkswagen", "country": "Germany", "model": "Tiguan", "body_type": "suv", "segment": "premium"},
    {"maker": "Volkswagen", "country": "Germany", "model": "Golf GTI", "body_type": "hatchback", "segment": "premium"},
    # Renault (France)
    {"maker": "Renault", "country": "France", "model": "Kwid", "body_type": "hatchback", "segment": "entry"},
    {"maker": "Renault", "country": "France", "model": "Triber", "body_type": "muv", "segment": "economy"},
    {"maker": "Renault", "country": "France", "model": "Kiger", "body_type": "suv", "segment": "economy"},
    {"maker": "Renault", "country": "France", "model": "Duster", "body_type": "suv", "segment": "mid"},
    # Nissan (Japan)
    {"maker": "Nissan", "country": "Japan", "model": "Magnite", "body_type": "suv", "segment": "economy"},
    {"maker": "Nissan", "country": "Japan", "model": "X-Trail", "body_type": "suv", "segment": "premium"},
    # MG Motor (United Kingdom)
    {"maker": "MG Motor", "country": "United Kingdom", "model": "Comet EV", "body_type": "hatchback", "segment": "ev"},
    {"maker": "MG Motor", "country": "United Kingdom", "model": "Astor", "body_type": "suv", "segment": "mid"},
    {"maker": "MG Motor", "country": "United Kingdom", "model": "Hector", "body_type": "suv", "segment": "mid"},
    {"maker": "MG Motor", "country": "United Kingdom", "model": "Hector Plus", "body_type": "muv", "segment": "mid"},
    {"maker": "MG Motor", "country": "United Kingdom", "model": "ZS EV", "body_type": "suv", "segment": "ev"},
    {"maker": "MG Motor", "country": "United Kingdom", "model": "Gloster", "body_type": "suv", "segment": "premium"},
    # Citroen (France)
    {"maker": "Citroen", "country": "France", "model": "C3", "body_type": "hatchback", "segment": "economy"},
    {"maker": "Citroen", "country": "France", "model": "C3 Aircross", "body_type": "suv", "segment": "economy"},
    {"maker": "Citroen", "country": "France", "model": "Basalt", "body_type": "suv", "segment": "mid"},
    {"maker": "Citroen", "country": "France", "model": "eC3", "body_type": "hatchback", "segment": "ev"},
    # Jeep (United States)
    {"maker": "Jeep", "country": "United States", "model": "Compass", "body_type": "suv", "segment": "mid"},
    {"maker": "Jeep", "country": "United States", "model": "Meridian", "body_type": "suv", "segment": "premium"},
    {"maker": "Jeep", "country": "United States", "model": "Wrangler", "body_type": "suv", "segment": "premium"},
    # Volvo (Sweden)
    {"maker": "Volvo", "country": "Sweden", "model": "XC40", "body_type": "suv", "segment": "premium"},
    {"maker": "Volvo", "country": "Sweden", "model": "XC40 Recharge", "body_type": "suv", "segment": "ev"},
    {"maker": "Volvo", "country": "Sweden", "model": "XC60", "body_type": "suv", "segment": "luxury"},
    {"maker": "Volvo", "country": "Sweden", "model": "XC90", "body_type": "suv", "segment": "luxury"},
    # BMW (Germany)
    {"maker": "BMW", "country": "Germany", "model": "3 Series", "body_type": "sedan", "segment": "premium"},
    {"maker": "BMW", "country": "Germany", "model": "5 Series", "body_type": "sedan", "segment": "luxury"},
    {"maker": "BMW", "country": "Germany", "model": "X1", "body_type": "suv", "segment": "premium"},
    {"maker": "BMW", "country": "Germany", "model": "X3", "body_type": "suv", "segment": "premium"},
    {"maker": "BMW", "country": "Germany", "model": "X5", "body_type": "suv", "segment": "luxury"},
    {"maker": "BMW", "country": "Germany", "model": "i4", "body_type": "sedan", "segment": "ev"},
    # Mercedes-Benz (Germany)
    {"maker": "Mercedes-Benz", "country": "Germany", "model": "A-Class Limousine", "body_type": "sedan", "segment": "premium"},
    {"maker": "Mercedes-Benz", "country": "Germany", "model": "C-Class", "body_type": "sedan", "segment": "premium"},
    {"maker": "Mercedes-Benz", "country": "Germany", "model": "E-Class", "body_type": "sedan", "segment": "luxury"},
    {"maker": "Mercedes-Benz", "country": "Germany", "model": "GLA", "body_type": "suv", "segment": "premium"},
    {"maker": "Mercedes-Benz", "country": "Germany", "model": "GLC", "body_type": "suv", "segment": "premium"},
    {"maker": "Mercedes-Benz", "country": "Germany", "model": "EQB", "body_type": "suv", "segment": "ev"},
    # Audi (Germany)
    {"maker": "Audi", "country": "Germany", "model": "A4", "body_type": "sedan", "segment": "premium"},
    {"maker": "Audi", "country": "Germany", "model": "Q3", "body_type": "suv", "segment": "premium"},
    {"maker": "Audi", "country": "Germany", "model": "Q5", "body_type": "suv", "segment": "premium"},
    {"maker": "Audi", "country": "Germany", "model": "Q8 e-tron", "body_type": "suv", "segment": "ev"},
    # Lexus (Japan)
    {"maker": "Lexus", "country": "Japan", "model": "ES", "body_type": "sedan", "segment": "luxury"},
    {"maker": "Lexus", "country": "Japan", "model": "NX", "body_type": "suv", "segment": "luxury"},
    # Jaguar Land Rover (United Kingdom)
    {"maker": "Jaguar Land Rover", "country": "United Kingdom", "model": "Range Rover Evoque", "body_type": "suv", "segment": "luxury"},
    {"maker": "Jaguar Land Rover", "country": "United Kingdom", "model": "Discovery Sport", "body_type": "suv", "segment": "luxury"},
    {"maker": "Jaguar Land Rover", "country": "United Kingdom", "model": "Range Rover", "body_type": "suv", "segment": "luxury"},
    # Mini (United Kingdom)
    {"maker": "Mini", "country": "United Kingdom", "model": "Cooper", "body_type": "hatchback", "segment": "premium"},
    {"maker": "Mini", "country": "United Kingdom", "model": "Countryman", "body_type": "suv", "segment": "premium"},
    # Porsche (Germany)
    {"maker": "Porsche", "country": "Germany", "model": "Macan", "body_type": "suv", "segment": "luxury"},
    {"maker": "Porsche", "country": "Germany", "model": "Cayenne", "body_type": "suv", "segment": "luxury"},
    {"maker": "Porsche", "country": "Germany", "model": "Taycan", "body_type": "sedan", "segment": "ev"},
    # Isuzu (Japan)
    {"maker": "Isuzu", "country": "Japan", "model": "D-Max V-Cross", "body_type": "pickup", "segment": "mid"},
    {"maker": "Isuzu", "country": "Japan", "model": "MU-X", "body_type": "suv", "segment": "premium"},
    # Force Motors (India)
    {"maker": "Force Motors", "country": "India", "model": "Gurkha", "body_type": "suv", "segment": "mid"},
    # BYD (China)
    {"maker": "BYD", "country": "China", "model": "Atto 3", "body_type": "suv", "segment": "ev"},
    {"maker": "BYD", "country": "China", "model": "Seal", "body_type": "sedan", "segment": "ev"},
    {"maker": "BYD", "country": "China", "model": "e6", "body_type": "muv", "segment": "ev"},
]
