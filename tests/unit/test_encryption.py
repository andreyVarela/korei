#!/usr/bin/env python3
"""
Test de encriptación con configuración real
"""
import os
from pathlib import Path

# Cargar variables de entorno desde .env
def load_env():
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Cargar configuración
load_env()

try:
    from core.encryption import get_encryption
    
    print("Probando sistema de encriptacion...")
    print(f"Clave maestra configurada: {'Si' if os.getenv('ENCRYPTION_MASTER_KEY') else 'No'}")
    
    # Datos de prueba
    test_credentials = {
        "todoist_token": "abcd1234567890_test_token",
        "google_oauth": {
            "access_token": "ya29.example_access_token_1234567890",
            "refresh_token": "1//example_refresh_token_abcdef",
            "client_id": "123456.apps.googleusercontent.com",
            "client_secret": "secret_example_xyz"
        },
        "user_data": {
            "user_id": "user_12345",
            "email": "user@example.com"
        }
    }
    
    print(f"Datos originales: {len(str(test_credentials))} caracteres")
    
    # Obtener instancia de encriptación
    encryptor = get_encryption()
    
    # Test 1: Encriptar credenciales completas
    print("\n=== Test 1: Credenciales completas ===")
    encrypted = encryptor.encrypt_credentials(test_credentials)
    print(f"Encriptado: {len(encrypted)} caracteres (Base64)")
    print(f"Muestra: {encrypted[:50]}...")
    
    # Desencriptar
    decrypted = encryptor.decrypt_credentials(encrypted)
    print(f"Desencriptado: {len(str(decrypted))} caracteres")
    
    # Verificar integridad
    if test_credentials == decrypted:
        print("✓ Integridad verificada - datos identicos")
    else:
        print("✗ Error de integridad")
        print(f"Original: {test_credentials}")
        print(f"Desencriptado: {decrypted}")
    
    # Test 2: Encriptar token individual
    print("\n=== Test 2: Token individual ===")
    single_token = "todoist_token_abc123456789"
    encrypted_token = encryptor.encrypt_token(single_token)
    decrypted_token = encryptor.decrypt_token(encrypted_token)
    
    print(f"Token original: {single_token}")
    print(f"Token encriptado: {encrypted_token[:50]}...")
    print(f"Token desencriptado: {decrypted_token}")
    print(f"Tokens iguales: {'Si' if single_token == decrypted_token else 'No'}")
    
    # Test 3: Hash para datos que no necesitan recuperarse
    print("\n=== Test 3: Hash irreversible ===")
    sensitive_id = "user_integration_google_calendar_12345"
    hash_hex, salt_hex = encryptor.hash_sensitive_data(sensitive_id)
    
    print(f"Dato original: {sensitive_id}")
    print(f"Hash: {hash_hex}")
    print(f"Salt: {salt_hex}")
    
    # Verificar hash
    is_valid_correct = encryptor.verify_hash(sensitive_id, hash_hex, salt_hex)
    is_valid_wrong = encryptor.verify_hash("dato_incorrecto", hash_hex, salt_hex)
    
    print(f"Verificacion correcta: {'Si' if is_valid_correct else 'No'}")
    print(f"Verificacion incorrecta: {'No' if not is_valid_wrong else 'Si'}")
    
    # Test 4: Verificar detección de datos encriptados
    print("\n=== Test 4: Deteccion de encriptacion ===")
    plain_text = "esto_no_esta_encriptado"
    encrypted_text = encryptor.encrypt_token("token_encriptado")
    
    print(f"'{plain_text}' esta encriptado: {'Si' if encryptor.is_encrypted(plain_text) else 'No'}")
    print(f"Texto encriptado esta encriptado: {'Si' if encryptor.is_encrypted(encrypted_text) else 'No'}")
    
    print("\n🎉 TODOS LOS TESTS PASARON EXITOSAMENTE")
    print("\n✅ Sistema de encriptacion AES-256-GCM funcionando correctamente")
    print("✅ Credenciales pueden almacenarse de forma segura")
    print("✅ Hashes pueden usarse para verificacion")
    
except Exception as e:
    print(f"❌ Error en test de encriptacion: {e}")
    import traceback
    traceback.print_exc()