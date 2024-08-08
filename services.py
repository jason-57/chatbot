import requests
import sett
import json
import time
import re

from datetime import datetime
from databases import DatabaseManager

def obtener_Mensaje_whatsapp(message):
    if 'type' not in message :
        text = 'mensaje no reconocido'
        return text

    typeMessage = message['type']
    if typeMessage == 'text':
        text = message['text']['body']
    elif typeMessage == 'button':
        text = message['button']['text']
    elif typeMessage == 'interactive' and message['interactive']['type'] == 'list_reply':
        text = message['interactive']['list_reply']['title']
    elif typeMessage == 'interactive' and message['interactive']['type'] == 'button_reply':
        text = message['interactive']['button_reply']['title']
    else:
        text = 'mensaje no procesado'
    
    
    return text

def enviar_Mensaje_whatsapp(data):
    try:
        whatsapp_token = sett.whatsapp_token
        whatsapp_url = sett.whatsapp_url
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer ' + whatsapp_token}
        print("se envia ", data)
        response = requests.post(whatsapp_url, 
                                 headers=headers, 
                                 data=data)
        
        if response.status_code == 200:
            return 'mensaje enviado', 200
        else:
            return 'error al enviar mensaje', response.status_code
    except Exception as e:
        return e,403
    
def text_Message(number,text):
    data = json.dumps(
            {
                "messaging_product": "whatsapp",    
                "recipient_type": "individual",
                "to": number,
                "type": "text",
                "text": {
                    "body": text
                }
            }
    )
    return data

def buttonReply_Message(number, options, body, footer, sedd,messageId):
    buttons = []
    for i, option in enumerate(options):
        buttons.append(
            {
                "type": "reply",
                "reply": {
                    "id": sedd + "_btn_" + str(i+1),
                    "title": option
                }
            }
        )

    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "buttons": buttons
                }
            }
        }
    )
    return data

def listReply_Message(number, options, body, footer, sedd,messageId):
    rows = []
    for i, option in enumerate(options):
        rows.append(
            {
                "id": sedd + "_row_" + str(i+1),
                "title": option,
                "description": ""
            }
        )

    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "button": "Ver Opciones",
                    "sections": [
                        {
                            "title": "Secciones",
                            "rows": rows
                        }
                    ]
                }
            }
        }
    )
    return data

def document_Message(number, url, caption, filename):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "link": url,
                "caption": caption,
                "filename": filename
            }
        }
    )
    return data

def sticker_Message(number, sticker_id):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "sticker",
            "sticker": {
                "id": sticker_id
            }
        }
    )
    return data

def get_media_id(media_name , media_type):
    media_id = ""
    if media_type == "sticker":
        media_id = sett.stickers.get(media_name, None)
    #elif media_type == "image":
    #    media_id = sett.images.get(media_name, None)
    #elif media_type == "video":
    #    media_id = sett.videos.get(media_name, None)
    #elif media_type == "audio":
    #    media_id = sett.audio.get(media_name, None)
    return media_id

def replyReaction_Message(number, messageId, emoji):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "reaction",
            "reaction": {
                "message_id": messageId,
                "emoji": emoji
            }
        }
    )
    return data

def replyText_Message(number, messageId, text):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "context": { "message_id": messageId },
            "type": "text",
            "text": {
                "body": text
            }
        }
    )
    return data

def markRead_Message(messageId):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id":  messageId
        }
    )
    return data

def administrar_chatbot(text,number, messageId, name, timestamp):
    db_manager = DatabaseManager() #instanciamos el objeto
    db_type = 'postgresql' # previamente configuramos solo mysql y postgresql
    conn = db_manager.connect(db_type)
    text = text.lower() #mensaje que envio el usuario
    list = []
    print("mensaje del usuario: ",text)

    markRead = markRead_Message(messageId)
    list.append(markRead)
    time.sleep(2)

    if "hola" in text:
        body = "¡Hola! 👋 Bienvenido al área de soporte técnico Redsis, por favor indícanos tu nombre:?"
        footer = "Redsis, su aliado estratégico."  
        nombre = textMessage   
        list.append(textMessage) 

    elif "nombre:" in text:
        body = f"¡Hola! {nombre}. ¿Cómo podemos ayudarte hoy?"
        footer = "Redsis, su aliado estratégico."
        options = ["🆕Generar Nuevo Ticket", "🔎Consultar Ticket"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed1",messageId)
        replyReaction = replyReaction_Message(number, messageId, "")
        list.append(replyReaction)
        list.append(replyButtonData)
    elif "generar nuevo ticket" in text:
        body = f"👌Perfecto, para crear un nuevo ticket por favor indícanos el área a la que perteneces."
        footer = "Redsis, su aliado estratégico."
        options = ["1.Comercial","2.Sistemas","3.Recursos Humanos","4.Atención Al Cliente"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed1",messageId)
        replyReaction = replyReaction_Message(number, messageId, "")
        area = re.search("\\d.(.*)", text, re.IGNORECASE).group(1).strip()  # extraemos el area
        list.append(replyReaction)
        list.append("area:"+replyButtonData)

    elif "area:" in text:
        body = f"👌Perfecto, Por favor selecciona el tipo de ticket que deseas generar:"
        footer = "Redsis, su aliado estratégico."
        options = ["1.Incidente","2.Solicitud"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed1",messageId)
        replyReaction = replyReaction_Message(number, messageId, "")
        tipoticket= re.search("\\d.(.*)", text, re.IGNORECASE).group(1).strip()  # extraemos el tipo de incidente
        list.append(replyReaction)
        list.append("tipoticket:"+replyButtonData)

    elif "tipoticket:" in text:
        body = f"👌Perfecto, Selecciona la prioridad para tu solicitud:"
        footer = "Redsis, su aliado estratégico."
        options = ["1.Bajo","2.Medio","3.Alto","4.Urgente"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed1",messageId)
        replyReaction = replyReaction_Message(number, messageId, "")
        prioridad = re.search("\\d.(.*)", text, re.IGNORECASE).group(1).strip()  # extraemos la prioridad
        list.append(replyReaction)
        list.append("prioridad:"+replyButtonData)

    elif "prioridad:" in text:
        textMessage = text_Message(number, f"👌Perfecto, ingresa el título de tu {tipoticket}:")        
        footer = "Redsis, su aliado estratégico."  
        titulo=textMessage      
        list.append("titulo:"+textMessage)

    elif "titulo:" in text:
        textMessage = text_Message(number, f"👌Perfecto, por favor ingresa una breve descripción de tu {tipoticket}:")        
        footer = "Redsis, su aliado estratégico."  
        descripcion=textMessage      
        list.append("descripcion:"+textMessage)

    elif "descripcion:" in text:
        description = re.search("descripcion:(.*)", text, re.IGNORECASE).group(1).strip()  # extraemos la descripción del incidente
        created_at = datetime.fromtimestamp(timestamp)  
        ticket_id = db_manager.generate_next_ticket_id(db_type, conn) 

        db_manager.create_ticket(db_type, conn, ticket_id, 'Nuevo', created_at, number, name, description)  
        body = f"Muchas gracias por la información, la solicitud fue abierta con el siguiente número de ticket {ticket_id}, con una prioridad {prioridad} y será atendida a la mayor brevedad posible"
        footer = "Redsis, su aliado estratégico."
        options = ["✔️Sí", "❌No, gracias"]
        replyButtonData = buttonReply_Message(number, 
                                              options, 
                                              body, 
                                              footer, "sed4",messageId)
        list.append(replyButtonData)

    elif "no, gracias" in text:
        textMessage = text_Message(number,"No dudes en contactarnos si tienes más solicitudes. Hasta luego!")
        list.append(textMessage)
    else :
        body = "Lo siento, no entendí lo que dijiste. Quieres que te ayude con alguna de estas opciones?"
        footer = "Redsis, su aliado estratégico."
        options = ["🆕Generar Nuevo Ticket", "🔎Consultar Ticket"]              

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed1",messageId)
        replyReaction = replyReaction_Message(number, messageId, "")
        list.append(replyReaction)
        list.append(replyButtonData)

    for item in list:
        enviar_Mensaje_whatsapp(item)
    db_manager.disconnect(db_type, conn)

