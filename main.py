from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler
import telegram.error
import requests
import csv


TOKEN = "7989936409:AAG13c0HT6X2_PoItB76y62UqqLokffXlFY"
BOT_USERNAME = "@t212tracker_bot"
ASKING_API_KEY = "Pedido"
port = "https://demo.trading212.com/api/v0/equity/portfolio"
pies = "https://demo.trading212.com/api/v0/equity/pies"
cash = "https://live.trading212.com/api/v0/equity/account/cash"



def load_database(file_path):
    user_data = {}
    try:
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                user_data[row['user_id']] = {'api_key': row['api_key'], 'regists': row['regists']}
    except FileNotFoundError:
        print("Database file not found, starting with an empty set.")
    return user_data

def save_database(file_path, user_data):
    fieldnames = ['user_id', 'api_key', 'regists']
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for user_id, data in user_data.items():
            writer.writerow({'user_id': user_id, 'api_key': data['api_key'], 'regists': data['regists']})

db_file = "bd.csv"  
user_database = load_database(db_file)


async def handle_message(update: Update, context):
    user_id = str(update.message.from_user.id)
    state = context.user_data.get('state')
    if str(update.message.from_user.id) not in user_database:
        user_database[str(update.message.from_user.id)] = {'api_key': '', 'regists': ''}
        save_database(db_file, user_database)


    try:
        if state == ASKING_API_KEY:
            api_key = update.message.text
            context.user_data['api_key'] = api_key
            user_database[user_id] = {'api_key': api_key, 'regists': ''}
            save_database(db_file, user_database)
            context.user_data.clear()
            await update.message.reply_text("Ótimo, podemos prosseguir.")
        else:
            await update.message.reply_text("Por favor, use o comando /registar_api para iniciar o registro.")
        
    except telegram.error.BadRequest as e:
        print(f"Error: {e}")

async def start_command(update: Update, context):
    if str(update.message.from_user.id) not in user_database:
        user_database[str(update.message.from_user.id)] = {'api_key': '', 'regists': ''}
        save_database(db_file, user_database)
        
    await update.message.reply_text("Bem-vindo(a) ao T212 Tracker, vou te ajudar a acompanhar o teu portfolio no T212. Primeiramente envia /registar_api para adicionares a api da tua conta T212. Para isso tens de ir à aplicação do T212, definições, depois API(BETA), generate API key se ainda não tiveres uma. Depois de ter a chave, envia-a para mim e vamos começar.")

async def registapi_command(update: Update, context):
    user_id = str(update.message.from_user.id)

    if user_id not in user_database:
        user_database[user_id] = {'api_key': '', 'regists': ''}
        save_database(db_file, user_database)
    await update.message.reply_text("Para adicionares a chave API tens de ir à aplicação do T212, definições, depois API(BETA), generate API key se ainda não tiveres uma e selecionas 'Account Data'. Depois de ter a chave, envia-a para mim e vamos começar.")
    context.user_data['state'] = ASKING_API_KEY
    await update.message.reply_text("Digita a tua chave de API.")

async def total_command(update: Update, context):
    user_id = str(update.message.from_user.id)
    if user_id not in user_database:
        user_database[user_id] = {'api_key': '', 'regists': []}
        save_database(db_file, user_database)
        
    if user_database[user_id]["api_key"] != "":
        headers = {"Authorization": user_database[user_id]["api_key"]}
        response = requests.get(cash, headers=headers)
        data = response.json()
        total = data["total"]
        ppl = data["ppl"]
        sign = "+" if ppl > 0 else "-"
        emoji = "💸" if ppl > 0 else "😢"
        message = f"Total: {total}€ | PNL: {sign}{abs(ppl)}% {emoji}"
        
        # Adicionar o total ao campo 'regists'
        user_database[user_id]['regists'].append(total)
        save_database(db_file, user_database)
        
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("Não tens nenhuma chave de API registada. Faz /registar_api para registar.")

        

if __name__ == "__main__":
    print("Starting")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('registar_api', registapi_command))
    app.add_handler(CommandHandler('total', total_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling(poll_interval=1)
    print("Polling...")