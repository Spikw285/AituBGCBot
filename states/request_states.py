from aiogram.fsm.state import State, StatesGroup

class GameRequestFSM(StatesGroup):
    choosing_game = State()     # Пользователь выбирает игру из списка
    entering_date = State()     # Ввод желаемой даты
    entering_comment = State()  # Опциональный комментарий для ГМа
    confirming = State()        # Подтверждение перед отправкой

class GMRequestFSM(StatesGroup):
    choosing_need = State()     # "Порекомендуй игру" и "Объясни правила"
    choosing_game = State()     # если "Объясни правила", пользователь выбирает игры, опционально
    entering_notes = State()    # Свободный текст
    confirming = State()

class TTRPGSignupFSM(StatesGroup):
    choosing_session = State()  # Выбор кампании или ваншота из открытых
    entering_notes = State()    # О себе: опыт, желания (опционально)
    entering_comment = State()
    confirming = State()