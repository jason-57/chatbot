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
        body = "隆Hola! 馃憢 Bienvenido a Soporte Bigdateros. 驴C贸mo podemos ayudarte hoy?"
        footer = "Equipo Bigdateros"
        options = ["馃帿 generar ticket", "馃攳 ver estado ticket", "馃攧 actualizar ticket"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed1",messageId)
        replyReaction = replyReaction_Message(number, messageId, "馃")
        list.append(replyReaction)
        list.append(replyButtonData)
    elif "generar ticket" in text:
        textMessage = text_Message(number,"Buena elecci贸n! Por favor ingresa su consulta con el siguiente formato: \n\n*'Ingresar Incidente:  <Ingresa breve descripci贸n del problema>*' \n\n Para que nuestros analistas lo revisen 馃槉")
        list.append(textMessage)
    elif "ingresar incidente" in text:
        description = re.search("ingresar incidente:(.*)", text, re.IGNORECASE).group(1).strip()  # extraemos la descripci贸n del incidente
        created_at = datetime.fromtimestamp(timestamp)  
        ticket_id = db_manager.generate_next_ticket_id(db_type, conn) 

        db_manager.create_ticket(db_type, conn, ticket_id, 'Nuevo', created_at, number, name, description)  
        body = f"Perfecto, se gener贸 el ticket *{ticket_id}*, en breves se estar谩n comunicando contigo. \n\n驴Deseas realizar otra consulta?"
        footer = "Equipo Bigdateros"
        options = ["鉁?S铆", "鉀?No, gracias"]
        replyButtonData = buttonReply_Message(number, 
                                              options, 
                                              body, 
                                              footer, "sed4",messageId)
        list.append(replyButtonData)
    elif "s铆" in text:
        body = "驴C贸mo podemos ayudarte hoy?"
        footer = "Equipo Bigdateros"
        options = ["馃帿 generar ticket", "馃攳 ver estado ticket", "馃攧 actualizar ticket"]
        replyButtonData = buttonReply_Message(number, options, body, footer, "sed1",messageId)
        list.append(replyButtonData)
    elif "ver estado ticket" in text:
        textMessage = text_Message(number,"Buen铆sima elecci贸n! Para verificar su estado ingresa el siguiente formato:\n\n*Buscar TKXXX* \n\n ")
        list.append(textMessage)
    elif  "buscar tk" in text:
        # extraemos el id del ticket
        ticket_id = re.search("buscar (tk.*)", text, re.IGNORECASE).group(1).upper().strip() 
        status = db_manager.get_ticket(db_type, conn,ticket_id)  
        if status == None:
            body = f"Lo siento, no se encontr茅 el ticket *{ticket_id}*.\n\n驴Deseas realizar otra consulta?"
        else :
            body =  f"Perfecto, el ticket *{ticket_id}* se encuentra en {status}. \n\n驴Deseas realizar otra consulta?"
        footer = "Equipo Bigdateros"
        options = ["鉁?S铆", "鉀?No, gracias"]
        replyButtonData = buttonReply_Message(number, 
                                              options, 
                                              body, 
                                              footer, "sed4",messageId)
        list.append(replyButtonData)
    elif "actualizar ticket" in text:
        textMessage = text_Message(number,"De acuerdo, Por favor ingresa el siguiente formato:\n\n*Actualizar TKXXX: <Breve descripci贸n a actualizar>*. ")
        list.append(textMessage)
    elif  "actualizar tkt" in text:
        match = re.search("actualizar (tkt.*): (.*)", text, re.IGNORECASE) 
        ticket_id = match.group(1).upper().strip()
        descripcion_actualizada = match.group(2).strip()
        updated = db_manager.update_ticket(db_type, conn, ticket_id, descripcion_actualizada)

        if updated:
            body = f"Perfecto, se actualiz贸n el ticket *{ticket_id}*. \n\n驴Deseas realizar otra consulta?"
        else:
            body = f"Lo siento, no se encontr贸 el ticket *{ticket_id}*.\n\n驴Deseas realizar otra consulta?"
        footer = "Equipo Bigdateros"
        options = ["鉁?S铆", "鉀?No, gracias"]
        replyButtonData = buttonReply_Message(number, options, body, footer, "sed4",messageId)
        list.append(replyButtonData)
    elif "no, gracias." in text:
        textMessage = text_Message(number,"Perfecto! No dudes en contactarnos si tienes m谩s preguntas. 隆Hasta luego! 馃槉")
        list.append(textMessage)
    else :
        data = text_Message(number,"Lo siento, no entend铆 lo que dijiste. 驴Quieres que te ayude con alguna de estas opciones?")
        list.append(data)

    for item in list:
        enviar_Mensaje_whatsapp(item)
    db_manager.disconnect(db_type, conn)

