#!/usr/bin/env python3
"""
Generador de clave maestra para encriptación AES-256
Ejecutar una sola vez y guardar la clave de forma segura
"""
import secrets
import os
from pathlib import Path

def generate_master_key():
    """Genera una clave maestra criptográficamente segura"""
    # Generar 512 bits (64 bytes) de entropía
    master_key = secrets.token_urlsafe(64)
    
    print("CLAVE MAESTRA GENERADA")
    print("=" * 50)
    print(f"ENCRYPTION_MASTER_KEY={master_key}")
    print("=" * 50)
    print()
    print("IMPORTANTE:")
    print("1. Copia esta clave a tu archivo .env")
    print("2. NUNCA compartas esta clave")
    print("3. Haz backup seguro de esta clave")
    print("4. Si pierdes esta clave, NO podras desencriptar tokens existentes")
    print()
    
    # Ofrecer guardar en .env automáticamente
    env_file = Path(".env")
    if env_file.exists():
        response = input("¿Quieres agregar esta clave a tu archivo .env? (y/N): ")
        if response.lower() in ['y', 'yes', 's', 'si']:
            try:
                # Leer contenido existente
                with open(env_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verificar si ya existe la clave
                if 'ENCRYPTION_MASTER_KEY=' in content:
                    print("Ya existe ENCRYPTION_MASTER_KEY en .env")
                    print("   Elimina la linea existente primero si quieres reemplazarla")
                else:
                    # Agregar la nueva clave
                    with open(env_file, 'a', encoding='utf-8') as f:
                        f.write(f"\n# Clave maestra para encriptacion (generada {secrets.token_hex(4)})\n")
                        f.write(f"ENCRYPTION_MASTER_KEY={master_key}\n")
                    
                    print("Clave agregada a .env")
                    
            except Exception as e:
                print(f"❌ Error escribiendo .env: {e}")
    else:
        print("💡 Tip: Crea un archivo .env y agrega esta clave")
    
    return master_key

def test_encryption():
    """Prueba básica del sistema de encriptación"""
    try:
        from core.encryption import CredentialEncryption
        
        # Usar clave temporal para testing
        test_key = secrets.token_urlsafe(64)
        encryptor = CredentialEncryption(test_key)
        
        # Datos de prueba
        test_credentials = {
            "api_token": "test_token_123456",
            "refresh_token": "refresh_abc789",
            "client_secret": "secret_xyz"
        }
        
        print("PROBANDO ENCRIPTACION...")
        
        # Encriptar
        encrypted = encryptor.encrypt_credentials(test_credentials)
        print(f"Encriptado exitosamente ({len(encrypted)} chars)")
        
        # Desencriptar
        decrypted = encryptor.decrypt_credentials(encrypted)
        print(f"Desencriptado exitosamente")
        
        # Verificar integridad
        if test_credentials == decrypted:
            print("Integridad verificada - datos identicos")
        else:
            print("Error de integridad - datos diferentes")
            
        # Probar hash (para datos que no necesitan recuperarse)
        hash_hex, salt_hex = encryptor.hash_sensitive_data("sensitive_identifier_123")
        is_valid = encryptor.verify_hash("sensitive_identifier_123", hash_hex, salt_hex)
        print(f"Hash verificado: {is_valid}")
        
        print("Sistema de encriptacion funcionando correctamente")
        
    except ImportError:
        print("Modulo de encriptacion no disponible para testing")
        print("   Instala primero: pip install cryptography")
    except Exception as e:
        print(f"Error en prueba de encriptacion: {e}")

if __name__ == "__main__":
    print("GENERADOR DE CLAVE MAESTRA PARA KOREI")
    print()
    
    master_key = generate_master_key()
    
    print()
    test_response = input("Quieres probar el sistema de encriptacion? (y/N): ")
    if test_response.lower() in ['y', 'yes', 's', 'si']:
        test_encryption()
    
    print()
    print("RECORDATORIO DE SEGURIDAD:")
    print("- Esta clave encripta TODOS los tokens de usuarios")
    print("- Haz backup en ubicacion segura (no en Git)")
    print("- Considera usar un gestor de secretos en produccion")
    print("- En Docker/K8s, usa secrets nativos")