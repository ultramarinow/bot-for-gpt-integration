from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import asyncio
import sqlite3

from config import TOKEN, bot, DATABASE_NAME
import database

dp = Dispatcher()


class resume_state(StatesGroup):
    data = State()


@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext) -> None:
    tg = message.from_user.id

    with sqlite3.connect('data.db') as conn:
        cur = conn.cursor()
        cur.execute('INSERT INTO users (tg) VALUES (?)', (tg,))
        conn.commit()

    text = (
        'Здравствуйте! Отправьте сообщение по следующей форме:'
        '\nВажно! указывать информацию строго до запятой - пример 1. +71111111111 example@gmail.com,'
        '\n'
        '\n1. ФИО'
        '\n2. Контактная информация (телефон, email)'
        '\n3. Образование (учебное заведение, специальность, годы обучения)'
        '\n4. Опыт работы (места работы, должности, обязанности)'
        '\n5. Навыки (профессиональные навыки, soft skills)'
        '\n6. Дополнительные сведования (курсы, сертификаты, хобби)'
    )

    await bot.send_message(
        chat_id=tg,
        text=text
    )

    await state.set_state(resume_state.data)
    
    
@dp.message(resume_state.data)
async def resume(message: types.Message, state: FSMContext) -> None:

    tg = message.from_user.id
    user_message = message.text

    for index, char in enumerate(user_message):
        try:
            if char.isdigit() and user_message[index + 1] in ('.'):
                actual_index = int(char)
                actual_str = []  ## Собираем строку от 1. до 2. (Алексеев Алексей Алексеевич для ФИО)
                print(actual_index)

            elif char.isalpha() or char.isdigit() or char in ('@', '+'):
                actual_str.append(char)
                if user_message[index + 1] in (' '):
                    actual_str.append(' ')

            elif char in ('.') and user_message[index + 1] == 'c':
                actual_str.append(char)
                if user_message[index + 1] in (' '):
                    actual_str.append(' ')

            elif char in (','):
                SQLarguments = ('fullname', 'contacts', 'education', 'job_exp', 'skills', 'additional')
                final_str = ""

                for char in actual_str:
                    final_str = final_str + char

                with sqlite3.connect('data.db') as conn:
                    cur = conn.cursor()
                    cur.execute(f'UPDATE users SET {SQLarguments[actual_index - 1]} = ? WHERE tg = ?', (final_str, tg))
                    conn.commit()
                    cur.execute('SELECT * FROM users')
                    print(cur.fetchall())
        except:
            await bot.send_message(
                chat_id=tg,
                text='Произошла ошибка. Возможно - вы не поставили запятые.\n'
                     'Заполните форму, где строки соответствуют этому примеру:\n'
                     '1. Информация,\n'
                     '2. Информация,'
            )

    with sqlite3.connect('data.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE tg = ?', (tg,))
    info_for_gpt = cur.fetchall()[0]

    prompt = ('Ты — опытный специалист по составлению резюме. '
              'Тебе нужно создать профессиональное резюме на основе предоставленных данных. Используй следующие поля:'
              '\n'
              '\nПример:'
              '\n1. ФИО: [ФИО]'
              '\n2. Контактная информация: [телефон, email]'
              '\n3. Образование: [учебное заведение, специальность, годы обучения]'
              '\n4. Опыт работы: [места работы, должности, обязанности]'
              '\n5. Навыки: [профессиональные навыки, soft skills]'
              '\n6. Дополнительные сведения: [курсы, сертификаты, хобби]'
              '\n'
              '\nИнформация, с которой тебе нужно создать резюме:'
              f'\n{info_for_gpt[1]}'
              f'\n{info_for_gpt[2]}'
              f'\n{info_for_gpt[3]}'
              f'\n{info_for_gpt[4]}'
              f'\n{info_for_gpt[5]}'
              f'\n{info_for_gpt[6]}'
    )
    await message.reply(prompt)
    await bot.send_message(
        chat_id=tg,
        text='Это вывод для отладки - в конечной версии бота сообщение отправляться не будет и останется только место для интеграции GPT'
    )
    """
    место для интеграции GPT
    """


async def main() -> None:

    with sqlite3.connect(DATABASE_NAME) as conn:
        database.create_tables(conn)
        
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
