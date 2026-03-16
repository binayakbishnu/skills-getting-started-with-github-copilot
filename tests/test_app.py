import pytest
from src.app import activities


class TestRoot:
    def test_root_redirects_to_static_index(self, client):
        # Arrange
        expected_redirect = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_redirect


class TestGetActivities:
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        # Arrange
        expected_activity_names = set(activities.keys())
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert set(data.keys()) == expected_activity_names
    
    def test_activity_has_required_fields(self, client, reset_activities):
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        for activity_name, activity_data in data.items():
            assert set(activity_data.keys()) == required_fields
            assert isinstance(activity_data["participants"], list)


class TestSignUp:
    def test_signup_successful(self, client, reset_activities):
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        initial_count = len(activities[activity]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity}"
        assert len(activities[activity]["participants"]) == initial_count + 1
        assert email in activities[activity]["participants"]
    
    def test_signup_duplicate_email_returns_400(self, client, reset_activities):
        # Arrange
        activity = "Chess Club"
        email = activities[activity]["participants"][0]  # Get existing participant
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up"
    
    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Nonexistent Activity"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestUnregister:
    def test_unregister_successful(self, client, reset_activities):
        # Arrange
        activity = "Chess Club"
        email = activities[activity]["participants"][0]
        initial_count = len(activities[activity]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity}"
        assert len(activities[activity]["participants"]) == initial_count - 1
        assert email not in activities[activity]["participants"]
    
    def test_unregister_not_registered_returns_400(self, client, reset_activities):
        # Arrange
        activity = "Chess Club"
        email = "notregistered@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student not registered for this activity"
    
    def test_unregister_nonexistent_activity_returns_404(self, client, reset_activities):
        # Arrange
        email = "student@mergington.edu"
        activity = "Nonexistent Activity"
        
        # Act
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestIntegration:
    def test_signup_then_unregister_flow(self, client, reset_activities):
        # Arrange
        email = "integration@mergington.edu"
        activity = "Programming Class"
        initial_count = len(activities[activity]["participants"])
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert signup successful
        assert signup_response.status_code == 200
        assert email in activities[activity]["participants"]
        
        # Act - Unregister
        unregister_response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        
        # Assert unregister successful
        assert unregister_response.status_code == 200
        assert len(activities[activity]["participants"]) == initial_count
        assert email not in activities[activity]["participants"]
