from dataclasses import dataclass
from typing import List, Dict, Set
import math
from collections import defaultdict

@dataclass
class User:
    user_id: int
    name: str
    interests: Set[str]
    latitude: float
    longitude: float

class RecommendationSystem:
    def __init__(self):
        self.users = {}
        self.interest_index = defaultdict(set)
        self.current_id = 1
    
    def add_user(self, user: User) -> None:
        """Add a new user to the system"""
        self.users[user.user_id] = user
        for interest in user.interests:
            self.interest_index[interest.lower()].add(user.user_id)
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1 = math.radians(lat1), math.radians(lon1)
        lat2, lon2 = math.radians(lat2), math.radians(lon2)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def calculate_interest_similarity(self, user1: User, user2: User) -> float:
        """Calculate interest similarity using Jaccard similarity"""
        intersection = len(user1.interests & user2.interests)
        union = len(user1.interests | user2.interests)
        return intersection / union if union > 0 else 0
    
    def get_recommendations(self, user_id: int, max_distance: float = 10, min_similarity: float = 0.2, 
                          limit: int = 10) -> List[Dict]:
        """Get personalized recommendations for a user"""
        if user_id not in self.users:
            raise ValueError("User not found")
            
        target_user = self.users[user_id]
        candidates = set()
        
        for interest in target_user.interests:
            candidates.update(self.interest_index[interest.lower()])
        
        candidates.discard(user_id)
        
        recommendations = []
        for candidate_id in candidates:
            candidate = self.users[candidate_id]
            
            distance = self.calculate_distance(
                target_user.latitude, target_user.longitude,
                candidate.latitude, candidate.longitude
            )
            
            if distance > max_distance:
                continue
                
            similarity = self.calculate_interest_similarity(target_user, candidate)
            
            if similarity < min_similarity:
                continue
                
            recommendations.append({
                'user_id': candidate.user_id,
                'name': candidate.name,
                'distance': round(distance, 2),
                'similarity': round(similarity, 2),
                'common_interests': list(target_user.interests & candidate.interests)
            })
        
        recommendations.sort(key=lambda x: (-x['similarity'], x['distance']))
        return recommendations[:limit]

def get_valid_float(prompt: str, min_val: float = None, max_val: float = None) -> float:
    """Helper function to get valid float input"""
    while True:
        try:
            value = float(input(prompt))
            if min_val is not None and value < min_val:
                print(f"Value must be at least {min_val}")
                continue
            if max_val is not None and value > max_val:
                print(f"Value must be at most {max_val}")
                continue
            return value
        except ValueError:
            print("Please enter a valid number")

def get_valid_int(prompt: str, min_val: int = None, max_val: int = None) -> int:
    """Helper function to get valid integer input"""
    while True:
        try:
            value = int(input(prompt))
            if min_val is not None and value < min_val:
                print(f"Value must be at least {min_val}")
                continue
            if max_val is not None and value > max_val:
                print(f"Value must be at most {max_val}")
                continue
            return value
        except ValueError:
            print("Please enter a valid integer")

def main():
    rs = RecommendationSystem()
    
    while True:
        print("\n=== Interest-Based Local Recommendation System ===")
        print("1. Add new user")
        print("2. Get recommendations")
        print("3. List all users")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == "1":
            print("\n--- Adding New User ---")
            name = input("Enter name: ").strip()
            
            # Get interests
            print("\nEnter interests (comma-separated):")
            print("Example: hiking, photography, cooking")
            interests_input = input().strip()
            interests = {interest.strip().lower() for interest in interests_input.split(",") if interest.strip()}
            
            # Get location
            print("\nEnter location coordinates:")
            print("(Latitude range: -90 to 90, Longitude range: -180 to 180)")
            latitude = get_valid_float("Latitude: ", -90, 90)
            longitude = get_valid_float("Longitude: ", -180, 180)
            
            # Create and add new user
            new_user = User(rs.current_id, name, interests, latitude, longitude)
            rs.add_user(new_user)
            print(f"\nUser added successfully! User ID: {rs.current_id}")
            rs.current_id += 1
            
        elif choice == "2":
            if not rs.users:
                print("\nNo users in the system yet. Please add users first.")
                continue
                
            print("\n--- Get Recommendations ---")
            print("Available users:")
            for user_id, user in rs.users.items():
                print(f"ID: {user_id}, Name: {user.name}")
            
            user_id = get_valid_int("\nEnter user ID to get recommendations: ")
            
            if user_id not in rs.users:
                print("User ID not found!")
                continue
            
            max_distance = get_valid_float("Enter maximum distance (km): ", 0)
            min_similarity = get_valid_float("Enter minimum similarity (0-1): ", 0, 1)
            limit = get_valid_int("Enter maximum number of recommendations: ", 1)
            
            try:
                recommendations = rs.get_recommendations(
                    user_id, 
                    max_distance=max_distance,
                    min_similarity=min_similarity,
                    limit=limit
                )
                
                if not recommendations:
                    print("\nNo recommendations found matching the criteria.")
                else:
                    print(f"\nRecommendations for {rs.users[user_id].name}:")
                    for rec in recommendations:
                        print(f"\nName: {rec['name']}")
                        print(f"Distance: {rec['distance']} km")
                        print(f"Similarity: {rec['similarity'] * 100:.1f}%")
                        print(f"Common interests: {', '.join(rec['common_interests'])}")
                        
            except ValueError as e:
                print(f"Error: {e}")
                
        elif choice == "3":
            if not rs.users:
                print("\nNo users in the system yet.")
            else:
                print("\n--- All Users ---")
                for user_id, user in rs.users.items():
                    print(f"\nID: {user_id}")
                    print(f"Name: {user.name}")
                    print(f"Interests: {', '.join(user.interests)}")
                    print(f"Location: ({user.latitude}, {user.longitude})")
                    
        elif choice == "4":
            print("\nThank you for using the recommendation system!")
            break
            
        else:
            print("\nInvalid choice. Please enter a number between 1 and 4.")

if __name__ == "__main__":
    main()
