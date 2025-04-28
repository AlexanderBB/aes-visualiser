# AES Visualiser 🔒✨

Интерактивно приложение за визуализация на базови AES операции (AddRoundKey, SubBytes, ShiftRows) стъпка по стъпка.  
Деплойнато като AWS Lambda функция с Function URL, базирано на Flask.

## 📋 Основни характеристики

- Преобразуване на текстови входове в AES матрици
- Показване на всяка криптографска стъпка с обяснения
- Семпъл и чист фронтенд с Bootstrap
- Използва AWS Lambda + Flask през awsgi адаптер
- Поддържа автоматичен деплой чрез Bash скрипт

## 🛠️ Технологии

- Python 3.12
- Flask 2.3.3
- AWS Lambda (Function URL)
- AWS CLI за деплой

# 🚀 Бърз старт (AWS Lambda Деплой)

# 🎬 Демо

Може да видите работещо демо на приложението тук:

👉 [Живо демо на AES Visualiser](https://j6qc5l4lwzmvi56wqyidebrpwm0ydnaw.lambda-url.eu-west-1.on.aws/)

## 1. Предварителни изисквания

Уверете се, че имате инсталирано:

- Python 3.12+
- pip
- AWS CLI
- zip

И задължително:

- AWS CLI конфигуриран с валидни креденшъли чрез `aws configure`.

## 2. Клониране на проекта

```bash
git clone https://github.com/your-username/aes-visualiser.git
cd aes-visualiser
```

## 3. Деплой на Lambda (One-click)

1. Направете скрипта изпълним:

```bash
chmod +x full_deploy.sh
```

2. Стартирайте деплоя:

```bash
./full_deploy.sh
```

## 4. Резултат

След няколко секунди ще получите:

```bash
🎉 Full Smart Deployment Complete!
🌐 Your Lambda Function URL:
https://abcde12345.lambda-url.eu-west-1.on.aws/

✅ Test Passed! Server responded with HTTP 200
📄 Response content:
<!DOCTYPE html>
<html>...</html>
```

# 🧹 Структура на проекта

```bash
aes-visualiser/
├── app.py              # Основната логика на Flask приложението
├── templates/          # HTML шаблони
├── static/             # CSS/JS файлове
├── requirements.txt    # Python зависимости
├── full_deploy.sh      # Скрипт за автоматичен деплой
├── README.md           # Този файл
```

# ⚡ Troubleshooting

| Проблем                          | Решение                                           |
|:---------------------------------|:--------------------------------------------------|
| Missing AWS credentials          | Стартирайте `aws configure`                       |
| `No module named flask` в Lambda | Проверете дали Layer е правилно създаден          |
| `AccessDeniedException`          | Проверете дали IAM потребителят има нужните права |
| Function URL не връща нищо       | Изчакайте няколко секунди след първи деплой       |

# 👨‍💻 Автор

**Александър Бояджиев - [LinedIn](https://www.linkedin.com/in/aleksandar-boyadzhiev-59087871/)**

# 📄 Лиценз

Този проект е лицензиран под MIT License.