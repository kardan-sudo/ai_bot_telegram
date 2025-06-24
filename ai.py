"""Импорты для работы"""
import json
import tkinter as tk
from tkinter import filedialog
import base64
import os
from urllib.parse import quote_plus
import requests

# --- API URLs ---
TEXT_MODELS_URL = "https://text.pollinations.ai/models"
IMAGE_MODELS_URL = "https://image.pollinations.ai/models"
TEXT_GENERATION_OPENAI_URL = "https://text.pollinations.ai/openai" # OpenAI compatible endpoint
IMAGE_GENERATION_BASE_URL = "https://image.pollinations.ai/prompt/"

# --- Helper Functions ---
def fetch_models(url):
    """Получает список моделей с указанного URL."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()  # Вызовет исключение для плохих ответов (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе моделей: {e}")
        return []

def select_model_from_list(models_data, model_type="text"):
    """
    Позволяет пользователю выбрать модель из списка.
    Для текстовых моделей 'models_data' - это список словарей.
    Для моделей изображений 'models_data' - это список строк.
    """
    model_text = "Выберите модель для работы или введите 'отмена' для выхода(писать цифрой): \n"
    if not models_data:
        print("Список моделей пуст или не удалось загрузить.")
        return None

    if model_type == "text":
        for i, model in enumerate(models_data):
            model_text += f"{i + 1}. {model.get('name', 'N/A')} \
                - {model.get('description', 'N/A')} \n"
    elif model_type == "image":
        for i, model_name in enumerate(models_data):
            model_text += f"{i + 1}. {model_name} \n"
    return model_text

def get_image_path_gui():
    """Открывает диалоговое окно для выбора файла изображения."""
    root = tk.Tk()
    root.withdraw()  # Скрываем основное окно Tkinter
    file_path = filedialog.askopenfilename(
        title="Выберите фотографию",
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.webp"), ("All files", "*.*")]
    )
    root.destroy() # Закрываем tk окно после выбора, чтобы не зависало
    return file_path

def encode_image_to_base64(image_path):
    """Кодирует изображение в base64 строку."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Ошибка при кодировании изображения: {e}")
        return None

# --- Generation Functions ---

def generate_text_with_model(selected_model_details, prompt):
    """Генерация текста с использованием выбранной модели."""
    model_name = selected_model_details.get("name")

    # Формируем запрос в формате OpenAI
    messages = []
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model_name,
        "messages": messages
        # Можно добавить другие параметры OpenAI, 
        # если API их поддерживает (temperature, max_tokens и т.д.)
        # "temperature": 0.7,
        # "max_tokens": 150
    }

    print("\nОтправка запроса...")
    try:
        response = requests.post(TEXT_GENERATION_OPENAI_URL, json=payload, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        api_response = response.json()

        # Парсинг ответа (стандартный для OpenAI)
        if api_response.get("choices") and len(api_response["choices"]) > 0:
            generated_text = api_response["choices"][0].get("message", {}).get("content")
            return generated_text
        else:
            return f'Не удалось получить сгенерированный \
                текст из ответа API. \n Ответ API: {api_response}'

    except requests.exceptions.HTTPError as e:
        return f"Ошибка HTTP: {e.response.status_code} - {e.response.text}"
    except requests.exceptions.RequestException as e:
        return f"Ошибка при отправке запроса на генерацию текста: {e}"
    except json.JSONDecodeError:
        return f'Ошибка: Не удалось декодировать \
            JSON ответ от сервера. \n Текст ответа: {response.text}'


def generate_image_with_model(selected_image_model_name, prompt):
    """Генерация изображения с использованием выбранной модели."""

    encoded_prompt = quote_plus(prompt) # URL-кодирование промпта
    request_url = f"{IMAGE_GENERATION_BASE_URL}\
        {encoded_prompt}?model={selected_image_model_name}"
    print(f"\nОтправка запроса на: {request_url}")

    try:
        response = requests.get(request_url, stream=True) # stream=True для изображений
        response.raise_for_status()

        filename = f"generated_image_{selected_image_model_name}_{prompt[:20].replace(' ','_')}.png" # простое имя файла

        with open(filename, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return os.path.abspath(filename)
        
    except requests.exceptions.HTTPError as e:
        return f"Ошибка HTTP: {e.response.status_code} - {e.response.text}"
    except requests.exceptions.RequestException as e:
        return f"Ошибка при отправке запроса на генерацию изображения: {e}"

# --- Main Script Logic ---

def main():
    """
    Основная функция
    """
    while True:
        print("\nКуда вас направить?")
        print("1. Генерация текста")
        print("2. Генерация фотографии")
        print("3. Выход")

        choice = input("Ваш выбор: ").strip()

        if choice == '1':
            print("\nЗагрузка моделей для текста...")
            text_models = fetch_models(TEXT_MODELS_URL)
            if text_models:
                selected_text_model_details = select_model_from_list(text_models, "text")
                if selected_text_model_details:
                    #generate_text_with_model(selected_text_model_details)
                    pass
            else:
                print("Не удалось загрузить текстовые модели.")

        elif choice == '2':
            print("\nЗагрузка моделей для изображений...")
            image_models = fetch_models(IMAGE_MODELS_URL) # Это список строк
            if image_models:
                selected_image_model_name = select_model_from_list(image_models, "image")
                if selected_image_model_name:
                    pass
                    #generate_image_with_model(selected_image_model_name)
            else:
                print("Не удалось загрузить модели изображений.")

        elif choice == '3':
            print("До свидания!")
            break
        else:
            print("Неверный выбор. Пожалуйста, попробуйте снова.")

if __name__ == "__main__":
    main()
