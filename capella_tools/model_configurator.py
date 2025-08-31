import json
from pathlib import Path
from getpass import getpass
from IPython.display import display, Markdown
from urllib.parse import urlparse


CONFIG_FILE = Path.home() / ".secrets" / "model_configs.json"
CONFIG_FILE.parent.mkdir(exist_ok=True)

# model_configurator.py


def get_api_key():
    path = Path.home() / ".secrets" / "openai_api_key.txt"
    return path.read_text().strip() if path.exists() else None

def get_base_url():
    path = Path.home() / ".secrets" / "openai_api_base_url.txt"
    if not path.exists():
        return None
    url = path.read_text().strip()
    parsed = urlparse(url)
    return url if parsed.scheme and parsed.netloc else None

def get_model():
    path = Path.home() / ".secrets" / "openai_model.txt"
    return path.read_text().strip() if path.exists() else "gpt-4o"  # fallback default

def load_configs():
    if CONFIG_FILE.exists():
        with CONFIG_FILE.open() as f:
            return json.load(f)
    return {}

def save_configs(configs):
    with CONFIG_FILE.open("w") as f:
        json.dump(configs, f, indent=2)

def create_or_update_config():
    name = input("🔖 Enter configuration name (e.g., mistral): ").strip()
    model = input("🤖 Model name (e.g., mistral-7b-instruct): ").strip()
    base_url = input("🌐 Base URL (e.g., http://localhost:8080/v1): ").strip()
    api_key = getpass("🔐 API Key (or sk-noauth): ").strip()
    
    configs = load_configs()
    configs[name] = {
        "model": model,
        "base_url": base_url,
        "api_key": api_key
    }

    # Set as default?
    make_default = input("⭐ Set this config as default? (y/N): ").strip().lower() == "y"
    if make_default:
        configs["_default"] = name

    save_configs(configs)
    display(Markdown(f"✅ **Configuration `{name}` saved.**"))
    if make_default:
        display(Markdown(f"🌟 **Set as default configuration.**"))

def list_configs():
    configs = load_configs()
    if not configs:
        display(Markdown("❌ **No configurations found.**"))
        return

    default_name = configs.get("_default", "None")
    display(Markdown(f"### 📦 Saved Configurations (default: `{default_name}`)"))
    for name, config in configs.items():
        if name == "_default":
            continue
        display(Markdown(f"- `{name}` → model: `{config['model']}`, url: `{config['base_url']}`"))


