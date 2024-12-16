import psycopg2
import pymysql
import uuid


class DatabaseManager:
    def __init__(self):
        self.databases = [    
            {'type': 'postgresql', 'connection_str': 'dbname=tatto57_w3rk_s5rx user=tatto57 password=7QP5jxVvrKlny5TTc7mg7LaOXmDtqZUw host=dpg-ctcbasq3esus73bdiko0-a port=5432'},      
            {'type': 'mysql', 'connection_str': {'host':'dpg-cqp7ojqj1k6c73depklg-a', 'user':'tatto57_user', 'password':'v0ldDw380FnTPE7JnxIULAu5lffeHzOC', 'db':'tatto57', 'charset':'utf8mb4'}},
        ]

    def connect(self, db_type):
        db = next((db for db in self.databases if db['type'] == db_type), None)
        if db is None:
            print(f"No database of type {db_type} found")
            return None

        if db_type == 'postgresql':
            print('postgresql')
            return psycopg2.connect(db['connection_str'])
        elif db_type == 'mysql':
            return pymysql.connect(**db['connection_str'])
                

    def disconnect(self, db_type, conn):
        print('disconnect')
        if db_type == 'postgresql' or db_type == 'mysql' or db_type == 'mssql':
            conn.close()
        else:
            pass
    
    def create_ticket(self, db_type, conn, area, asunto, descripcion, prioridad, fecha, fecha_creación):
        if db_type == 'postgresql' or db_type == 'mysql' :
            cur = conn.cursor()
            query = f"INSERT INTO glpi_tickets (entities_id, name, content, priority, date, date_creation) VALUES ('{area}','{asunto}','{descripcion}','{prioridad}','{fecha}','{fecha_creación}') RETURNING id;"            
            cur.execute(query)
            ticket = cur.fetchone()
            conn.commit()
            cur.close()
            return ticket
        
    '''def list_area(self, db_type, conn):
        if db_type == 'postgresql' or db_type == 'mysql' :
            cur = conn.cursor()
            query = f"select * from areas"            
            cur.execute(query)
            areas=[]
            areas.append(cur.fetchall())
            
            conn.commit()
            cur.close()
            return areas'''
    def list_area(self, db_type, conn):
        if db_type == 'postgresql' or db_type == 'mysql' :
            cur = conn.cursor()
            query = f"SELECT * FROM areas"            
            cur.execute(query)
            areas=[]
            areas.append(cur.fetchall())
            print(f"estas son las areas: {areas})
            lista_areas= areas.replace("[","").replace("(","").replace(")","").replace("]","").replace(","," ").replace("\'","").split (" ")
            print(f"estas es la lista_areas"{lista_areas})
            conn.commit()
            cur.close()
            return lista_areas
            
    
    def get_ticket(self, db_type, conn, ticket_id):
        if db_type == 'postgresql' or db_type == 'mysql' :
            cur = conn.cursor()
            query = f"SELECT id FROM glpi_tickets WHERE id = '{ticket_id}'"
            cur.execute(query)
            result = cur.fetchone()
            cur.close()
            if result is not None:  # validamos en caso no exista el ticket
                return result[0]
            else:
                print(f"No se encontró ningún ticket con ID {ticket_id} en {db_type}.")
                return None
            