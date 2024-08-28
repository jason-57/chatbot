from flask import Flask, request, render_template
import sett 
import services

app = Flask(__name__)

dict_sesiones={}

def generar_dict(numero):
    dict_sesiones[str(numero)] = {"flujo": 0, "name_glpi": "", "area_glpi": "", "prioridad_glpi": "", "tipoticket_glpi": "", "titulo_glpi": "", "descripcion_glpi": "", "fechacreacion_glpi": "", }


@app.route('/webhook', methods=['GET'])
def verificar_token():
    try:
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if token == sett.token and challenge != None:
            return challenge
        else:
            return 'token incorrecto', 403
    except Exception as e:
        return e,403
    
@app.route('/webhook', methods=['POST'])
def recibir_mensajes():       
    try:              
        body = request.get_json()
        entry = body['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        message = value['messages'][0]
        number = message['from']
        messageId = message['id']
        contacts = value['contacts'][0]
        name = contacts['profile']['name']
        text = services.obtener_Mensaje_whatsapp(message)
        timestamp = int(message['timestamp'])
        
        if str(number) in dict_sesiones.keys():
            services.administrar_chatbot(text, number,messageId,name,timestamp)
            return 'enviado'
        else:
            generar_dict(number)
            services.administrar_chatbot(text, number,messageId,name,timestamp)
            return 'enviado'

    except Exception as e:
        return 'no enviado ' + str(e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
