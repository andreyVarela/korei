"""
Sistema de encriptación seguro para credenciales sensibles
Usa AES-256-GCM para encriptación autenticada
"""
import os
import json
import base64
from typing import Dict, Any, Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from loguru import logger


class CredentialEncryption:
    """
    Maneja encriptación/desencriptación de credenciales usando AES-256-GCM
    - AES-256: Encriptación simétrica militar
    - GCM: Modo autenticado (previene tampering)
    - PBKDF2: Key derivation con salt para mayor seguridad
    """
    
    def __init__(self, master_key: Optional[str] = None):
        """
        Inicializa el sistema de encriptación
        
        Args:
            master_key: Clave maestra. Si None, se toma de variable de entorno
        """
        self.master_key = master_key or os.getenv('ENCRYPTION_MASTER_KEY')
        
        if not self.master_key:
            raise ValueError(
                "ENCRYPTION_MASTER_KEY no configurada. "
                "Genera una con: python -c 'import secrets; print(secrets.token_urlsafe(64))'"
            )
        
        # Convertir master key a bytes
        self.master_key_bytes = self.master_key.encode('utf-8')
    
    def _derive_key(self, salt: bytes) -> bytes:
        """Deriva clave AES-256 usando PBKDF2"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=salt,
            iterations=100000,  # OWASP recomienda 100k+
            backend=default_backend()
        )
        return kdf.derive(self.master_key_bytes)
    
    def encrypt_credentials(self, credentials: Dict[str, Any]) -> str:
        """
        Encripta credenciales usando AES-256-GCM
        
        Args:
            credentials: Diccionario con credenciales sensibles
            
        Returns:
            String base64 con datos encriptados
        """
        try:
            # Convertir a JSON
            json_data = json.dumps(credentials, ensure_ascii=False)
            plaintext = json_data.encode('utf-8')
            
            # Generar salt y nonce únicos
            salt = os.urandom(16)  # 128 bits
            nonce = os.urandom(12)  # 96 bits para GCM
            
            # Derivar clave
            key = self._derive_key(salt)
            
            # Encriptar con AES-GCM
            aesgcm = AESGCM(key)
            ciphertext = aesgcm.encrypt(nonce, plaintext, None)
            
            # Combinar: salt + nonce + ciphertext
            encrypted_data = salt + nonce + ciphertext
            
            # Codificar en base64 para almacenamiento
            return base64.b64encode(encrypted_data).decode('ascii')
            
        except Exception as e:
            logger.error(f"Error encriptando credenciales: {e}")
            raise
    
    def decrypt_credentials(self, encrypted_data: str) -> Dict[str, Any]:
        """
        Desencripta credenciales
        
        Args:
            encrypted_data: String base64 con datos encriptados
            
        Returns:
            Diccionario con credenciales originales
        """
        try:
            # Decodificar base64
            data = base64.b64decode(encrypted_data.encode('ascii'))
            
            # Extraer componentes: salt(16) + nonce(12) + ciphertext(resto)
            salt = data[:16]
            nonce = data[16:28]
            ciphertext = data[28:]
            
            # Derivar clave
            key = self._derive_key(salt)
            
            # Desencriptar
            aesgcm = AESGCM(key)
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            
            # Convertir de JSON
            json_data = plaintext.decode('utf-8')
            return json.loads(json_data)
            
        except Exception as e:
            logger.error(f"Error desencriptando credenciales: {e}")
            raise
    
    def encrypt_token(self, token: str) -> str:
        """Encripta un token individual"""
        return self.encrypt_credentials({"token": token})
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """Desencripta un token individual"""
        data = self.decrypt_credentials(encrypted_token)
        return data["token"]
    
    def is_encrypted(self, data: str) -> bool:
        """Verifica si un string está encriptado (base64 válido)"""
        try:
            decoded = base64.b64decode(data.encode('ascii'))
            return len(decoded) >= 28  # Mínimo: salt(16) + nonce(12)
        except:
            return False
    
    @staticmethod
    def generate_master_key() -> str:
        """Genera una clave maestra segura"""
        import secrets
        return secrets.token_urlsafe(64)  # 512 bits de entropía
    
    def hash_sensitive_data(self, data: str, salt: Optional[bytes] = None) -> tuple[str, str]:
        """
        Hash con SHA-256 para datos que NO necesitan ser recuperados
        Útil para verificación de integridad o identificadores únicos
        
        Args:
            data: Datos a hashear
            salt: Salt opcional (si None, se genera uno nuevo)
            
        Returns:
            Tupla (hash_hex, salt_hex)
        """
        if salt is None:
            salt = os.urandom(32)  # 256 bits
        
        # Crear hash con salt
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(salt)
        digest.update(data.encode('utf-8'))
        hash_bytes = digest.finalize()
        
        return hash_bytes.hex(), salt.hex()
    
    def verify_hash(self, data: str, hash_hex: str, salt_hex: str) -> bool:
        """Verifica un hash SHA-256"""
        try:
            salt = bytes.fromhex(salt_hex)
            computed_hash, _ = self.hash_sensitive_data(data, salt)
            return computed_hash == hash_hex
        except:
            return False


# Instancia singleton con lazy loading
_encryption_instance = None

def get_encryption() -> CredentialEncryption:
    """Obtiene instancia singleton de encriptación"""
    global _encryption_instance
    if _encryption_instance is None:
        _encryption_instance = CredentialEncryption()
    return _encryption_instance


# Funciones de conveniencia
def encrypt_credentials(credentials: Dict[str, Any]) -> str:
    """Función de conveniencia para encriptar"""
    return get_encryption().encrypt_credentials(credentials)

def decrypt_credentials(encrypted_data: str) -> Dict[str, Any]:
    """Función de conveniencia para desencriptar"""
    return get_encryption().decrypt_credentials(encrypted_data)