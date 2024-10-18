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
        self.users = {}  # user_id -> User
        self.interest_index = defaultdict(set)  # interest -> set of user_ids
        
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
        """
        Get personalized recommendations for a user
        Args:
            user_id: ID of the user seeking recommendations
            max_distance: Maximum distance in kilometers
            min_similarity: Minimum interest similarity threshold
            limit: Maximum number of recommendations to return
        """
        if user_id not in self.users:
            raise ValueError("User not found")
            
        target_user = self.users[user_id]
        candidates = set()
        
        # Find users with at least one common interest
        for interest in target_user.interests:
            candidates.update(self.interest_index[interest.lower()])
        
        # Remove the target user from candidates
        candidates.discard(user_id)
        
        recommendations = []
        for candidate_id in candidates:
            candidate = self.users[candidate_id]
            
            # Calculate distance
            distance = self.calculate_distance(
                target_user.latitude, target_user.longitude,
                candidate.latitude, candidate.longitude
            )
            
            # Skip if too far
            if distance > max_distance:
                continue
                
            # Calculate interest similarity
            similarity = self.calculate_interest_similarity(target_user, candidate)
            
            # Skip if similarity is too low
            if similarity < min_similarity:
                continue
                
            recommendations.append({
                'user_id': candidate.user_id,
                'name': candidate.name,
                'distance': round(distance, 2),
                'similarity': round(similarity, 2),
                'common_interests': list(target_user.interests & candidate.interests)
            })
        
        # Sort by similarity score and distance
        recommendations.sort(key=lambda x: (-x['similarity'], x['distance']))
        
        return recommendations[:limit]

# Example usage
def main():
    rs = RecommendationSystem()
    
    # Add sample users
    users = [
        User(1, "Alice", {"hiking", "photography", "cooking"}, 40.7128, -74.0060),  # NYC
        User(2, "Bob", {"hiking", "camping", "photography"}, 40.7214, -73.9977),    # NYC
        User(3, "Charlie", {"cooking", "gaming", "music"}, 40.7306, -73.9352),      # NYC
        User(4, "Diana", {"photography", "art", "music"}, 40.7505, -73.9934),       # NYC
        User(5, "Eve", {"hiking", "art", "cooking"}, 42.3601, -71.0589),           # Boston
    ]
    
    for user in users:
        rs.add_user(user)
    
    # Get recommendations for Alice
    recommendations = rs.get_recommendations(1, max_distance=5, min_similarity=0.2)
    
    print(f"Recommendations for Alice:")
    for rec in recommendations:
        print(f"\nName: {rec['name']}")
        print(f"Distance: {rec['distance']} km")
        print(f"Similarity: {rec['similarity'] * 100:.1f}%")
        print(f"Common interests: {', '.join(rec['common_interests'])}")

if __name__ == "__main__":
    main()