from flask import Flask, request, jsonify
import pyodbc
import openai
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

app = Flask(__name__)

# Configuración de la conexión
server = 'srvtfmsql.database.windows.net'
database = 'jossTFM'
username = 'cef'
password = 'Big@Data2024'
driver = '{ODBC Driver 17 for SQL Server}'

try:
    cnxn = pyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    cursor = cnxn.cursor()
    print("Conexión a la base de datos exitosa.")
except Exception as e:
    print(f"Error al conectar a la base de datos: {e}")

chatbot = ChatBot('SQLBot')

trainer = ListTrainer(chatbot)

try:
    cursor.execute("SELECT Pregunta, Respuesta FROM data_bot")
    rows = cursor.fetchall()

    for row in rows:
        trainer.train([row.Pregunta, row.Respuesta])
    print("Entrenamiento del chatbot completado.")
except Exception as e:
    print(f"Error al entrenar el chatbot: {e}")

def get_response_from_db(question):
    try:
        query = "SELECT Respuesta FROM data_bot WHERE Pregunta = ?"
        cursor.execute(query, question)
        row = cursor.fetchone()
        if row:
            return row.Respuesta
        else:
            return "Lo siento, no tengo una respuesta para esa pregunta."
    except Exception as e:
        return f"Error al obtener la respuesta de la base de datos: {e}"

# Configuración de Azure OpenAI
openai.api_key = 'YOUR_OPENAI_API_KEY'

def get_openai_response(question):
    response = openai.Completion.create(
        engine="text-davinci-003",  # O el modelo que estés utilizando
        prompt=question,
        max_tokens=150
    )
    return response.choices[0].text.strip()

@app.route('/chatbot', methods=['POST'])
def chatbot_response():
    user_input = request.json.get("question")
    response = get_response_from_db(user_input)
    if response == "Lo siento, no tengo una respuesta para esa pregunta.":
        response = get_openai_response(user_input)
    return jsonify({"response": str(response)})

if __name__ == '__main__':
    app.run()
