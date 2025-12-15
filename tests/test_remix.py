import unittest
from unittest.mock import MagicMock, patch
from src.remix_engine import Remixer

class TestRemixEngine(unittest.TestCase):
    @patch('src.remix_engine.anthropic.Anthropic')
    def test_remix_logic(self, mock_anthropic):
        # Setup Mock
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Here is a remixed post in Rahul's voice.")]
        mock_client.messages.create.return_value = mock_message
        
        # Test
        remixer = Remixer("fake_key")
        result = remixer.remix_content("Some viral transcript content here.")
        
        # Verify
        self.assertEqual(result, "Here is a remixed post in Rahul's voice.")
        
        # Verify System Prompt contains key phrases
        call_args = mock_client.messages.create.call_args[1]
        system_prompt = call_args['system']
        self.assertIn("RAHUL'S VOICE GUIDELINES", system_prompt)
        self.assertIn("Em Dashes", system_prompt)
        self.assertIn("Extended Vowels", system_prompt)

if __name__ == '__main__':
    unittest.main()
