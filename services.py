import requests
import sett
import json
import time
import re
import app

from datetime import datetime
from databases import DatabaseManager

#Variables globales para el control del chatbot


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
        textMessage = text_Message(number,"👋Bienvenido al área de soporte técnico Redsis\nPor favor indícanos tú nombre usando el siguiente formato:\n\n*Name: <Tú Nombre>*")        
        list.append(textMessage)

    elif "name:" in text:
        app.session["name_glpi"] = (re.search("name:(.*)", text, re.IGNORECASE).group(1).strip()).capitalize()  # extraemos el nombre
        #app.name_glpi = (re.search("(.*)", text, re.IGNORECASE).group(1).strip()).capitalize()  # extraemos el nombre
        body = f"¿Hola, {app.name_glpi} en que podemos ayudarte hoy?"
        footer = "Redsis su aliado estratégico"
        options = ["Generar Ticket", "Ver Estado Ticket"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed1",messageId)
        replyReaction = replyReaction_Message(number, messageId, "👍")
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "generar ticket" in text:        
        body = f"Perfecto {app.name_glpi}, para crear un nuevo ticket por favor indícanos el área a la que perteneces."
        footer = "Redsis su aliado estratégico"
        options = ["Comercial", "Sistemas", "Jurídica","Financiera", "Recursos Humanos"]
        
        replyListData = listReply_Message(number, options, body, footer, "sed1",messageId)
        replyReaction = replyReaction_Message(number, messageId, "👍")
        list.append(replyReaction)
        list.append(replyListData)
    
    elif "comercial" in text or "sistemas" in text or "jurídica" in text or "financiera" in text or "recursos humanos" in text:   
        app.session["area_glpi"] = (re.search("(.*)", text, re.IGNORECASE).group(1).strip()).capitalize()  # extraemos el area     
        body = f"{app.name_glpi} ahora por favor indícanos el tipo de ticket que deseas generar"
        footer = "Redsis su aliado estratégico"
        options = ["Incidente", "Requerimiento"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed1",messageId)
        replyReaction = replyReaction_Message(number, messageId, "👍")
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "incidente" in text or "requerimiento" in text:   
        app.session["prioridad_glpi"] = (re.search("(.*)", text, re.IGNORECASE).group(1).strip()).capitalize()  # extraemos el tipo de ticket     
        body = f"Perfecto! Ahora selecciona la prioridad para tu {app.tipoticket_glpi} según la urgencia con la que debe ser atendida:"
        footer = "Redsis su aliado estratégico"
        options = ["Baja", "Media","Alta"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed1",messageId)
        replyReaction = replyReaction_Message(number, messageId, "👍")
        list.append(replyReaction)
        list.append(replyButtonData)
        
    elif "baja" in text or "media" in text or "alta" in text:
        app.session["tipoticket_glpi"] = re.search("(.*)", text, re.IGNORECASE).group(1).strip()  # extraemos la prioridad de la solicitud
        textMessage = text_Message(number,f"{app.name_glpi} ingresa el encabezado de tu {app.tipoticket_glpi} usando el siguiente formato:\n\n*Title: <Título de tu {app.tipoticket_glpi}>*")        
        list.append(textMessage)
        
    elif "title:" in text:
        app.session["titulo_glpi"] = re.search("title:(.*)", text, re.IGNORECASE).group(1).strip()  # extraemos el titulo de la solicitud
        textMessage = text_Message(number,f"{app.name_glpi}, ahora ingresa una breve descripción de tu solicitud usando el siguiente formato:\n\n*Description: <Descripción de tu {app.tipoticket_glpi}>*")        
        list.append(textMessage)

    elif "description:" in text:
        app.session["descripcion_glpi"] = re.search("description:(.*)", text, re.IGNORECASE).group(1).strip()  # extraemos la descripción de la solicitud
        app.session["fechacreacion_glpi"] = datetime.fromtimestamp(timestamp)  
        ticket_id = db_manager.generate_next_ticket_id(db_type, conn) 

        db_manager.create_ticket(db_type, conn, ticket_id, 'Nuevo', app.fechacreacion_glpi, number, name, app.descripcion_glpi)  
        body = f"{app.name_glpi} se generó el ticket *{ticket_id}* para tú *{app.tipoticket_glpi}* \"*{app.titulo_glpi}*\" satisfactoriamente.👍 \n\nDeseas realizar otra consulta?"
        footer = "Redsis su aliado estratégico"
        options = ["✔️Sí", "❌No, gracias"]
        replyButtonData = buttonReply_Message(number, 
                                              options, 
                                              body, 
                                              footer, "sed4",messageId)
        list.append(replyButtonData)
    elif "sí" in text:
        body = f"{app.name_glpi} indicanos en que otra cosa podemos ayudarte hoy?"
        footer = "Redsis su aliado estratégico"
        options = ["generar ticket", "ver estado ticket", "actualizar ticket"]
        replyButtonData = buttonReply_Message(number, options, body, footer, "sed1",messageId)
        list.append(replyButtonData)
    elif "ver estado ticket" in text:
        textMessage = text_Message(number,f"{app.name_glpi} para verificar el estado de tu ticket ingresa su numero usando el siguiente formato:\n\n*Buscar TKTXXX* \n\n ")
        list.append(textMessage)
    elif  "buscar tkt" in text:
        # extraemos el id del ticket
        ticket_id = re.search("buscar (tkt.*)", text, re.IGNORECASE).group(1).upper().strip() 
        status = db_manager.get_ticket(db_type, conn,ticket_id)  
        if status == None:
            body = f"{app.name_glpi} lo siento, no se encontró el ticket *{ticket_id}*.\n\nDeseas realizar otra consulta?"
        else :
            body =  f"{app.name_glpi} el ticket *{ticket_id}* con asunto \" {app.titulo_glpi}\" creado en la fecha *{app.fechacreacion_glpi}* se encuentra en estado: *{status}* y nuestros técnicos estan trabajando para solucionarlo.\n\nDeseas realizar otra consulta?"
        footer = "Redsis su aliado estratégico"
        options = ["✔️Sí", "❌No, gracias"]
        replyButtonData = buttonReply_Message(number, 
                                              options, 
                                              body, 
                                              footer, "sed4",messageId)
        list.append(replyButtonData)

    elif "no, gracias" in text:
        textMessage = text_Message(number,"Perfecto! No dudes en contactarnos si tienes más preguntas.\n 🖐️Hasta luego!")
        list.append(textMessage)
    else :
        body = "Lo siento, no entendí lo que dijiste🤷. Quieres que te ayude con alguna de estas opciones?"
        footer = "Redsis su aliado estratégico"
        options = ["generar ticket", "ver estado ticket", "actualizar ticket"]
        replyButtonData = buttonReply_Message(number, options, body, footer, "sed1",messageId)
        list.append(replyButtonData)
    

    for item in list:
        enviar_Mensaje_whatsapp(item)
    db_manager.disconnect(db_type, conn)

