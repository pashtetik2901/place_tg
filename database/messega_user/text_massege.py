def text_in_card(title: str, address: str, link: str, point: str):
    if point != '':
        point = int(point)
        star = f'Оценка: '
        for i in range(point):
            star += '\u2B50'
    else:
        star = ''

    text = f'''<b>{title}</b>\n<i>{address}</i>\n<a href="{link}">Перейти по ссылке</a>\n{star}'''
    return text



def greeting(name: str):
    text = f'<b>Привет {name}!!!</b>\nЭто бот, где ты можешь формировать свой списко мест, которые хочешь посетить.\nТы можешь:\n 1) Добавлять новые места\n 2) Посмотреть список мест, которые ты добавил\n 3) Если ты не знаешь, куда сходить. Нажми кнопку <u>Куда сходить?</u> и я подскажу!'
    return text