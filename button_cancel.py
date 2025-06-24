"""Импорт types из telebot для работы с кнопками"""
from telebot import types

class CancelKeyboard:
    """Класс кнопки отмены"""
    @staticmethod
    def create():
        """Создает Reply-клавиатуру с кнопкой 'Отмена'"""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        cancel_btn = types.KeyboardButton("Отмена ❌")
        markup.add(cancel_btn)
        return markup

    @staticmethod
    def remove():
        """Убирает клавиатуру (например, после отмены)"""
        return types.ReplyKeyboardRemove()
