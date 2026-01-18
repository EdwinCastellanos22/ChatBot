from django.test import TestCase

from .models import Room, Message
# Create your tests here.

class RoomTestCase(TestCase):
    def setUp(self):
        self.room = Room.objects.create(name='Test Room')

    def test_room_creation(self):
        self.assertEqual(self.room.name, 'Test Room')
        

    def test_room_str_representation(self):
        self.assertEqual(str(self.room), 'Test Room')
        
class MessageTestCase(TestCase):
    def setUp(self):
        self.room = Room.objects.create(name='Test Room')
        self.message = Message.objects.create(
            room=self.room,
            content='This is a test message.'
        )

    def test_message_creation(self):
        self.assertEqual(self.message.content, 'This is a test message.')
        self.assertEqual(self.message.room, self.room)

    def test_message_str_representation(self):
        expected_str = f"[{self.room}] || [{self.message.user}] || [{self.message.content[:20]}]"
        self.assertEqual(str(self.message), expected_str)