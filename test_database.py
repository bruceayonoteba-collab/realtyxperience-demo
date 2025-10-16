from database import SessionLocal, create_user, get_user_by_username, create_property, get_user_properties, User
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def test_database():
    db = SessionLocal()
    
    try:
        print("=" * 50)
        print("TESTING DATABASE CONNECTION")
        print("=" * 50)
        
        print("\n1️⃣ Creating test user...")
        user = create_user(
            db,
            username="testuser123",
            email="test@example.com",
            password=hash_password("password123"),
            user_type="agent",
            test_group="A",
            phone="+2341234567890"
        )
        print(f"✅ User created: {user.username} (ID: {user.id})")
        
        print("\n2️⃣ Creating test property...")
        property = create_property(
            db,
            owner_id=user.id,
            title="Beautiful 3BR Apartment in Lekki",
            description="Spacious apartment",
            property_type="apartment",
            listing_type="rent",
            city="Lagos",
            state="Lagos",
            bedrooms=3,
            bathrooms=2,
            price=500000,
            currency="NGN"
        )
        print(f"✅ Property created: {property.title}")
        
        print("\n3️⃣ Retrieving data...")
        retrieved_user = get_user_by_username(db, "testuser123")
        properties = get_user_properties(db, user.id)
        print(f"✅ Found user: {retrieved_user.email}")
        print(f"✅ Found {len(properties)} property")
        
        print("\n4️⃣ Cleaning up test data...")
        db.delete(property)
        db.delete(user)
        db.commit()
        print("✅ Test data cleaned up")
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_database()
