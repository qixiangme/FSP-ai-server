import yaml
from pathlib import Path
from typing import Dict

class PromptManager:
    _instance = None
    _prompts: Dict[str, str] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PromptManager, cls).__new__(cls)
            cls._instance._load_prompts()
        return cls._instance

    def _load_prompts(self):
        """Load prompts from the yaml file."""
        # Assuming prompts.yaml is in the same directory as this file
        current_dir = Path(__file__).parent
        prompt_path = current_dir / "prompts.yaml"
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                self._prompts = data.get('prompts', {})
        except FileNotFoundError:
            print(f"Warning: Prompts file not found at {prompt_path}")
            self._prompts = {}
        except Exception as e:
            print(f"Error loading prompts: {e}")
            self._prompts = {}

    def get_prompt(self, key: str, default: str = "") -> str:
        """Retrieve a prompt by key."""
        return self._prompts.get(key, default)

    def reload(self):
        """Force reload of prompts from file."""
        self._load_prompts()

# Global instance
prompt_manager = PromptManager()
