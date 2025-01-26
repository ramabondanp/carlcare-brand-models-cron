import requests
import json
import os
import sys

def load_previous_models(filename='previous_models.json'):
    print(f"Loading previous models from {filename}")
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{filename} not found, returning an empty dictionary.")
        return {}

def find_new_models(current_models, previous_models):
    print("Finding new models...")
    new_models = {}
    for brand, models in current_models.items():
        prev_brand_models = previous_models.get(brand, [])
        print(f"Checking models for brand {brand}.")
        new_brand_models = [model for model in models if model not in prev_brand_models]
        if new_brand_models:
            new_models[brand] = new_brand_models
            print(f"New models found for {brand}")
    if not new_models:
        print("No new models found.")
    return new_models

def get_models_from_url(url):
    print(f"Fetching data from URL: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print("Data fetched successfully.")
        
        models_dict = {}
        for brand_item in data.get('list', []):
            brand = brand_item.get('brand', '')
            if brand not in models_dict:
                models_dict[brand] = []
            
            for series_item in brand_item.get('list', []):
                for model_item in series_item.get('list', []):
                    model = model_item.get('model')
                    if model:
                        models_dict[brand].append(model)
        
        return models_dict
    except Exception as e:
        print(f"Error fetching models: {e}")
        return {}

def post_to_telegram(new_models):
    print("Checking environment variables for bot_token and chat_id.")
    if 'bot_token' in os.environ and 'chat_id' in os.environ:
        bot_token, chat_id = os.environ['bot_token'], os.environ['chat_id']
        print("Environment variables found, proceeding to send message.")
    else:
        print("Error: Environment variables 'bot_token' and 'chat_id' are not set.")
        sys.exit(1)
    
    for brand, models in new_models.items():
        message = f"Found new models on the Carlcare website for {brand}: {', '.join(models)}"
        payload = {
            'chat_id': chat_id,
            'text': message
        }
        print(f"Sending message for {brand}")
        requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage', json=payload)

def main():
    print("Starting the main function.")
    url = "https://service.carlcare.com/CarlcareBg/spare-parts-price/brand-model-series?country=Indonesia"
    
    print("Fetching current models...")
    current_models = get_models_from_url(url)
    
    print("Loading previous models...")
    previous_models = load_previous_models()
    
    with open('models.json', 'w') as f:
        print("Saving current models to models.json")
        json.dump(current_models, f, indent=2)
    
    print("Comparing current models with previous models...")
    new_models = find_new_models(current_models, previous_models)
    
    if new_models:
        print("New models found, sending to Telegram.")
        post_to_telegram(new_models)
        
        print("Saving current models as previous models.")
        with open('previous_models.json', 'w') as f:
            json.dump(current_models, f, indent=2)
    else:
        print("No new models found. Nothing to send.")

if __name__ == '__main__':
    main()
