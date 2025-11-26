# Script para probar el sistema de auditoría
from database import Database

db = Database()

# Ver últimas 10 entradas de auditoría
print("\n=== ÚLTIMAS 10 ENTRADAS DE AUDITORÍA ===\n")
logs = db.obtener_auditoria(10)

if not logs:
    print("No hay registros de auditoría aún.")
else:
    for log in logs:
        print(f"[{log[1]}] {log[2]} en {log[3]} (ID: {log[4]})")
        print(f"  Usuario: {log[5]}")
        print(f"  Anterior: {log[6]}")
        if log[7]:
            print(f"  Nuevo: {log[7]}")
        print(f"  {log[8]}\n")
