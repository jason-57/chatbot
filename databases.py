import psycopg2
import pymysql
import uuid


class DatabaseManager:
    def __init__(self):
        self.databases = [    
            {'type': 'postgresql', 'connection_str': 'dbname=tatto57_w3rk user=tatto57 password=nFIXQbcueSbLMr4liGAU9Y8pEhua5IIJ host=dpg-crfhkrrgbbvc73c4ur4g-a port=5432'},      
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
    
    def create_ticket(self, db_type, conn, ticket_id, status, created_at, number, name, description):
        if db_type == 'postgresql' or db_type == 'mysql' :
            cur = conn.cursor()
            query = f"INSERT INTO tickets (ticket_id, status, created_at, number, name, description) VALUES ('{ticket_id}', '{status}', '{created_at}', '{number}', '{name}', '{description}')"
            cur.execute(query)
            conn.commit()
            cur.close()
        
    
    def get_ticket(self, db_type, conn, ticket_id):
        if db_type == 'postgresql' or db_type == 'mysql' :
            cur = conn.cursor()
            query = f"SELECT status FROM tickets WHERE ticket_id = '{ticket_id}'"
            cur.execute(query)
            result = cur.fetchone()
            cur.close()
            if result is not None:  # validamos en caso no exista el ticket
                return result[0]
            else:
                print(f"No se encontró ningún ticket con ID {ticket_id} en {db_type}.")
                return None
            

    def get_areas(self, db_type, conn):
        if db_type == 'postgresql' or db_type == 'mysql' :
            cur = conn.cursor()
            query = f"SELECT * FROM areas"
            cur.execute(query)
            result = cur.fetchall()
            cur.close()
            if result is not None:  # validamos en caso no existan areas
                return result[0]
            else:
                print(f"No se encontraron areas relacionadas")
                return None
            
        
    def update_ticket(self, db_type, conn, ticket_id, description):
        if db_type == 'postgresql' or db_type == 'mysql' :
            cur = conn.cursor()
            query = f"UPDATE tickets SET description = '{description}' WHERE ticket_id = '{ticket_id}'"
            cur.execute(query)
            conn.commit()
            updated_rows = cur.rowcount
            cur.close()
            return updated_rows > 0  # Devuelve True si se actualizó al menos una fila
        
    def generate_next_ticket_id(self, db_type, conn):
        last_ticket_id=''
        if db_type == 'postgresql' or db_type == 'mysql' :
            cur = conn.cursor()
            query = "SELECT ticket_id FROM tickets ORDER BY ticket_id DESC LIMIT 1"
            cur.execute(query)
            result = cur.fetchone()
            last_ticket_id = result[0] if result else "TKT000"  
            cur.close()
        
                
        last_number = int(last_ticket_id[3:])
        next_number = last_number + 1
        next_ticket_id = f"TKT{str(next_number).zfill(3)}"
        return next_ticket_id