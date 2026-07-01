"""Synthetic review content -- original templates, never copied from any real site.

`REVIEW_TEMPLATES[rating]` holds sentence templates for that star rating; each
contains a `{model}` placeholder filled in with the car model's name.
"""

REVIEWER_FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Krishna",
    "Ishaan", "Rohan", "Karan", "Rahul", "Amit", "Vikram", "Suresh", "Rajesh",
    "Ananya", "Diya", "Saanvi", "Aadhya", "Kavya", "Priya", "Neha", "Pooja",
    "Sneha", "Anjali", "Meera", "Divya", "Shreya", "Nikita", "Farhan", "Imran",
    "Zoya", "Ayesha", "Manoj", "Deepak", "Sanjay", "Ramesh", "Lakshmi", "Kiran",
]

RATING_DISTRIBUTION = {5: 0.35, 4: 0.30, 3: 0.20, 2: 0.10, 1: 0.05}

REVIEW_TEMPLATES = {
    5: [
        "Absolutely love my {model}. Mileage is excellent and the ride quality is fantastic.",
        "Best purchase decision ever. The {model} feels premium and drives beautifully.",
        "The {model} exceeded my expectations -- great features for the price.",
        "Superb build quality and a smooth engine. Highly recommend the {model}.",
        "Comfortable on long drives and easy to maintain. Very happy with the {model}.",
    ],
    4: [
        "The {model} is a solid choice overall, though the service cost could be lower.",
        "Good performance and decent mileage. The {model} has been reliable so far.",
        "Happy with the {model}, just wish the boot space was a bit bigger.",
        "Nice features and comfortable seats. The {model} handles well in city traffic.",
        "Overall satisfied with the {model} -- good value for money.",
    ],
    3: [
        "The {model} is okay -- does the job but nothing exceptional.",
        "Average experience with the {model}, interiors could be better for this price.",
        "The {model} rides fine but the after-sales service needs improvement.",
        "Decent car but I expected better mileage from the {model}.",
    ],
    2: [
        "Not fully satisfied with the {model} -- had some niggling issues in the first year.",
        "The {model} feels underpowered for highway driving.",
        "Service center experience for the {model} was disappointing.",
    ],
    1: [
        "Regret buying the {model}, faced multiple issues within months.",
        "Poor build quality on my {model} and slow service response.",
    ],
}
