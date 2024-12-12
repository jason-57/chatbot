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
    
def ext_ticket(cadena):
    ticket=""
    for item in cadena:
        if item.isnumeric():
            ticket+=item
    return ticket

def ext_areas(cadena):    
    areas=str(cadena)
    return areas
        
def administrar_chatbot(text,number, messageId, name, timestamp):
    
    db_manager = DatabaseManager() #instanciamos el objeto
    db_type = 'postgresql' # previamente configuramos solo mysql y postgresql
    conn = db_manager.connect(db_type)
    text = text.lower() #mensaje que envio el usuario
    list = []

    markRead = markRead_Message(messageId)
    list.append(markRead)
    time.sleep(1)
    print(f"nuevo estdo del diccionario {app.dict_sesiones}")
    
    

    if app.dict_sesiones[str(number)]['flujo'] == "0":
        app.dict_sesiones[str(number)]['flujo'] ="1"        
        textMessage = text_Message(number,f"Hola👋 bienvenido al área de soporte técnico Redsis🖥️\nPor favor indícanos tú nombre para poder atenderte.")        
        list.append(textMessage)

    elif app.dict_sesiones[str(number)]['flujo'] == "1":
        app.dict_sesiones[str(number)]['flujo'] ="2"
        app.dict_sesiones[str(number)]['name_glpi'] = str(text).capitalize()
        lst_areas=db_manager.list_area(db_type, conn)
        
        body = f"¿{app.dict_sesiones[str(number)]['name_glpi']} en que podemos ayudarte hoy?"
        footer = "Redsis su aliado estratégico"
        options=[]
        for item in lst_areas:
            options.append(str(item))   
        print(options) 
        replyButtonData = buttonReply_Message(number, options, body, footer, "sed1",messageId)
        replyReaction = replyReaction_Message(number, messageId, "👍")
        list.append(replyReaction)
        list.append(replyButtonData) 

    elif app.dict_sesiones[str(number)]['flujo'] == "2":
        
        if text=="generar ticket":
            app.dict_sesiones[str(number)]['flujo'] ="3"      
            body = f"📋Perfecto *{app.dict_sesiones[str(number)]['name_glpi']}*, para generar un nuevo ticket por favor indícanos el área a la que perteneces.🏢"
            footer = "Redsis su aliado estratégico"
            options = ["Sistemas", "Comercial", "Auditoria"] 
            replyListData = listReply_Message(number, options, body, footer, "sed1",messageId)
            replyReaction = replyReaction_Message(number, messageId, "👍")
            list.append(replyReaction)
            list.append(replyListData)

        elif text == "ver estado ticket":  
            app.dict_sesiones[str(number)]['flujo'] ="100"
            textMessage = text_Message(number,f"🔎 *{app.dict_sesiones[str(number)]['name_glpi']}* por favor ingresa el codigo del ticket (TKTXXX) que deseas verificar.\n\n ")
            list.append(textMessage)

        else:
            app.dict_sesiones[str(number)]['flujo'] ="2"
            body = "Lo siento, no entendí lo que dijiste🤷. Quieres que te ayude con alguna de estas opciones❓"
            footer = "Redsis su aliado estratégico"
            options = ["Generar Ticket", "Ver Estado Ticket"]
            replyButtonData = buttonReply_Message(number, options, body, footer, "sed1",messageId)
            list.append(replyButtonData)

    elif app.dict_sesiones[str(number)]['flujo'] == "3":
        if text=="sistemas" or text=="comercial" or text=="auditoria":
            #Consulta bd por el id del area y ese es el que se guarda
            app.dict_sesiones[str(number)]['flujo'] = "4"
            app.dict_sesiones[str(number)]['area_glpi']=str(text)
            body = f"*{app.dict_sesiones[str(number)]['name_glpi']}* ahora por favor indícanos el tipo de ticket que deseas generar📇"
            footer = "Redsis su aliado estratégico"
            options = ["Incidente", "Requerimiento"]

            replyButtonData = buttonReply_Message(number, options, body, footer, "sed1",messageId)
            replyReaction = replyReaction_Message(number, messageId, "👍")
            list.append(replyReaction)
            list.append(replyButtonData)
        else:
            app.dict_sesiones[str(number)]['flujo'] ="2"
            body = "Lo siento, no entendí lo que dijiste🤷. Quieres que te ayude con alguna de estas opciones❓"
            footer = "Redsis su aliado estratégico"
            options = ["Generar Ticket", "Ver Estado Ticket"]
            replyButtonData = buttonReply_Message(number, options, body, footer, "sed1",messageId)
            list.append(replyButtonData)
            

    elif app.dict_sesiones[str(number)]['flujo'] == "4":
        if text =="incidente" or text == "requerimiento":
            app.dict_sesiones[str(number)]['flujo'] = "5"
            app.dict_sesiones[str(number)]['tipoticket_glpi']=text
            body = f"Perfecto! Ahora selecciona la prioridad para tu *{app.dict_sesiones[str(number)]['tipoticket_glpi']}* según la urgencia con la que debe ser atendida🚨"
            footer = "Redsis su aliado estratégico"
            options = ["Baja", "Media","Alta"]

            replyButtonData = buttonReply_Message(number, options, body, footer, "sed1",messageId)
            replyReaction = replyReaction_Message(number, messageId, "👍")
            list.append(replyReaction)
            list.append(replyButtonData)
        else:
            app.dict_sesiones[str(number)]['flujo'] ="2"
            body = "Lo siento, no entendí lo que dijiste🤷. Quieres que te ayude con alguna de estas opciones❓"
            footer = "Redsis su aliado estratégico"
            options = ["Generar Ticket", "Ver Estado Ticket"]
            replyButtonData = buttonReply_Message(number, options, body, footer, "sed1",messageId)
            list.append(replyButtonData)
            
    
    elif app.dict_sesiones[str(number)]['flujo'] == "5":
        if text == "baja" or text == "media" or text == "alta":
            app.dict_sesiones[str(number)]['flujo'] = "6"
            app.dict_sesiones[str(number)]['prioridad_glpi']=text 
            textMessage = text_Message(number,f"*{app.dict_sesiones[str(number)]['name_glpi']}* ingresa el encabezado de tu *{app.dict_sesiones[str(number)]['tipoticket_glpi']}.*🔤\n")        
            list.append(textMessage)
        else:
            app.dict_sesiones[str(number)]['flujo'] ="2"
            body = "Lo siento, no entendí lo que dijiste🤷. Quieres que te ayude con alguna de estas opciones❓"
            footer = "Redsis su aliado estratégico"
            options = ["Generar Ticket", "Ver Estado Ticket"]
            replyButtonData = buttonReply_Message(number, options, body, footer, "sed1",messageId)
            list.append(replyButtonData)
            

    elif app.dict_sesiones[str(number)]['flujo'] == "6":
        app.dict_sesiones[str(number)]['flujo'] = "7"
        app.dict_sesiones[str(number)]['titulo_glpi'] = str(text).lower()
        textMessage = text_Message(number,f"*{app.dict_sesiones[str(number)]['name_glpi']}*, ahora ingresa una breve descripción de tu *{app.dict_sesiones[str(number)]['tipoticket_glpi']}*🔠\n")        
        list.append(textMessage)
    
    elif app.dict_sesiones[str(number)]['flujo'] == "7":
        app.dict_sesiones[str(number)]['flujo'] = "101"
        app.dict_sesiones[str(number)]['descripcion_glpi'] = str(text).lower()
        app.dict_sesiones[str(number)]['fechacreacion_glpi']=datetime.fromtimestamp(timestamp)        
        crear_ticket = db_manager.create_ticket(db_type, conn, app.dict_sesiones[str(number)]['area_glpi'], app.dict_sesiones[str(number)]['titulo_glpi'], app.dict_sesiones[str(number)]['descripcion_glpi'], app.dict_sesiones[str(number)]['prioridad_glpi'], app.dict_sesiones[str(number)]['fechacreacion_glpi'], app.dict_sesiones[str(number)]['fechacreacion_glpi'] )
        crear_ticket
        num_ticket=str(crear_ticket)
        ticket= ext_ticket(num_ticket)
        
        body = f"{app.dict_sesiones[str(number)]['name_glpi']} se generó el ticket #: *{ticket}* para tú *{app.dict_sesiones[str(number)]['tipoticket_glpi']}* \"*{app.dict_sesiones[str(number)]['titulo_glpi']}*\" satisfactoriamente.👍 \n\n¿Deseas realizar otra consulta?"
        footer = "Redsis su aliado estratégico"
        options = ["✔️Sí", "❌No, gracias"]
        replyButtonData = buttonReply_Message(number, options, body, footer, "sed4",messageId)
        list.append(replyButtonData) 

    elif app.dict_sesiones[str(number)]['flujo'] == "100":
        app.dict_sesiones[str(number)]['flujo'] = "101"
        ticket_id= str(text).upper()
        status = db_manager.get_ticket(db_type, conn, ticket_id)  

        if status == None:            
            body = f"{app.dict_sesiones[str(number)]['name_glpi']} lo siento😔, no se encontró el ticket *{ticket_id}*.\n\nDeseas realizar otra consulta?"  

        else :
            body =  f"📄{app.dict_sesiones[str(number)]['name_glpi']} el ticket *{ticket_id}* con asunto \" {app.dict_sesiones[str(number)]['titulo_glpi']}\" creado en la fecha *{app.dict_sesiones[str(number)]['fechacreacion_glpi']}* se encuentra en estado: *{status}* y nuestros técnicos estan trabajando para solucionarlo.\n\nDeseas realizar otra consulta?"
        footer = "Redsis su aliado estratégico"
        options = ["✔️Sí", "❌No, gracias"]
        replyButtonData = buttonReply_Message(number, options, body, footer, "sed4",messageId)
        list.append(replyButtonData)
    
    elif app.dict_sesiones[str(number)]['flujo'] == "101":
        if text == "✔️sí":
            app.dict_sesiones[str(number)]['flujo'] ="2"
            body = f"{app.dict_sesiones[str(number)]['name_glpi']} en que otra cosa te podemos colaborar?"
            footer = "Redsis su aliado estratégico"
            options = ["Generar Ticket", "Ver Estado Ticket"]
            replyButtonData = buttonReply_Message(number, options, body, footer, "sed1",messageId)
            list.append(replyButtonData)
            

        elif text == "❌no, gracias":
            textMessage = text_Message(number,"Perfecto! No dudes en contactarnos si tienes más preguntas.\n 🖐️Hasta luego!")
            list.append(textMessage)
            del(app.dict_sesiones[str(number)])

        else:
            app.dict_sesiones[str(number)]['flujo'] ="2"
            body = "Lo siento, no entendí lo que dijiste🤷. Quieres que te ayude con alguna de estas opciones❓"
            footer = "Redsis su aliado estratégico"
            options = ["Generar Ticket", "Ver Estado Ticket"]
            replyButtonData = buttonReply_Message(number, options, body, footer, "sed1",messageId)
            list.append(replyButtonData)
            

    for item in list:
        enviar_Mensaje_whatsapp(item)
    db_manager.disconnect(db_type, conn)

