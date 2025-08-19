"""
Servicio para comparación inteligente de nombres en transacciones
"""
import re
from typing import List, Dict, Any, Optional
from difflib import SequenceMatcher
from loguru import logger


class NameMatcher:
    """Clase para hacer matching fuzzy de nombres en transacciones"""
    
    def __init__(self):
        # Palabras comunes que no son parte del nombre
        self.noise_words = {
            'de', 'del', 'la', 'el', 'los', 'las', 'y', 'e', 'o', 'u',
            'señor', 'señora', 'sr', 'sra', 'don', 'doña', 'ing', 'dr', 'dra',
            'licenciado', 'licenciada', 'lic', 'prof', 'profesor', 'profesora'
        }
    
    def normalize_name(self, name: str) -> str:
        """Normaliza un nombre para comparación"""
        if not name:
            return ""
        
        # Convertir a minúsculas
        normalized = name.lower().strip()
        
        # Remover caracteres especiales pero mantener espacios
        normalized = re.sub(r'[^\w\s]', '', normalized)
        
        # Remover múltiples espacios
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized
    
    def extract_key_name_parts(self, name: str) -> List[str]:
        """Extrae las partes principales del nombre (nombres y apellidos importantes)"""
        normalized = self.normalize_name(name)
        words = normalized.split()
        
        # Filtrar palabras de ruido
        key_parts = [word for word in words if word not in self.noise_words and len(word) > 2]
        
        return key_parts
    
    def calculate_similarity(self, name1: str, name2: str) -> float:
        """Calcula similitud entre dos nombres usando múltiples métodos"""
        if not name1 or not name2:
            return 0.0
        
        # Normalizar nombres
        norm1 = self.normalize_name(name1)
        norm2 = self.normalize_name(name2)
        
        # Si son exactamente iguales después de normalizar
        if norm1 == norm2:
            return 1.0
        
        # Extraer partes clave
        parts1 = self.extract_key_name_parts(name1)
        parts2 = self.extract_key_name_parts(name2)
        
        if not parts1 or not parts2:
            return 0.0
        
        # Calcular similitud usando diferentes métodos
        similarities = []
        
        # 1. Similitud de texto completo
        full_similarity = SequenceMatcher(None, norm1, norm2).ratio()
        similarities.append(full_similarity)
        
        # 2. Similitud de partes clave (nombres/apellidos)
        part_matches = 0
        for part1 in parts1:
            best_match = 0
            for part2 in parts2:
                # Similitud exacta de palabras
                if part1 == part2:
                    best_match = 1.0
                    break
                # Similitud parcial de palabras
                else:
                    word_sim = SequenceMatcher(None, part1, part2).ratio()
                    if word_sim > best_match:
                        best_match = word_sim
            
            if best_match > 0.8:  # Solo contar matches fuertes
                part_matches += best_match
        
        if len(parts1) > 0:
            part_similarity = part_matches / len(parts1)
            similarities.append(part_similarity)
        
        # 3. Verificar si al menos 2 partes importantes coinciden
        strong_matches = 0
        for part1 in parts1:
            for part2 in parts2:
                if SequenceMatcher(None, part1, part2).ratio() > 0.85:
                    strong_matches += 1
                    break
        
        if strong_matches >= 2:
            similarities.append(0.9)
        
        # Retornar la mejor similitud
        return max(similarities) if similarities else 0.0
    
    def is_user_match(self, transaction_name: str, user_name: str, threshold: float = 0.75) -> bool:
        """Determina si el nombre en la transacción corresponde al usuario"""
        similarity = self.calculate_similarity(transaction_name, user_name)
        
        logger.info(f"NOMBRE_MATCH: '{transaction_name}' vs '{user_name}' = {similarity:.2f}")
        
        return similarity >= threshold
    
    def extract_names_from_transaction_text(self, text: str) -> List[str]:
        """Extrae posibles nombres de personas del texto de transacción"""
        # Patrones para encontrar nombres (mejorados)
        name_patterns = [
            r'(?:a|para|destinatario|receptor):\s*([A-Z][A-Z\s]+)',
            r'(?:de|desde|remitente|emisor):\s*([A-Z][A-Z\s]+)',
            r'(?:transferencia sinpe (?:móvil|movil) a)\s+([A-Z][A-Z\s]+?)(?:\s+por)',
            r'(?:transferencia sinpe (?:móvil|movil) de)\s+([A-Z][A-Z\s]+?)(?:\s+por)',
            r'(?:sinpe (?:móvil|movil) a)\s+([A-Z][A-Z\s]+?)(?:\s+por)',
            r'(?:sinpe (?:móvil|movil) de)\s+([A-Z][A-Z\s]+?)(?:\s+por)',
            r'(?:enviaste a|pagaste a)\s+([A-Z][A-Z\s]+?)(?:\s+por)',
            r'(?:recibiste de|cobro de)\s+([A-Z][A-Z\s]+?)(?:\s+por)',
            # Patrón más genérico para nombres en mayúsculas
            r'\b([A-Z]{2,}\s+[A-Z]{2,}(?:\s+[A-Z]{2,})*)\b',
        ]
        
        names = []
        text_upper = text.upper()
        
        for pattern in name_patterns:
            matches = re.findall(pattern, text_upper, re.IGNORECASE)
            for match in matches:
                # Limpiar el nombre
                clean_name = re.sub(r'[^\w\s]', '', match).strip()
                if len(clean_name) > 5:  # Filtrar nombres muy cortos
                    names.append(clean_name)
        
        return names
    
    def analyze_transaction_direction(self, text: str, user_name: str) -> Dict[str, Any]:
        """Analiza la dirección de una transacción basándose en el texto"""
        text_lower = text.lower()
        
        # Extraer nombres del texto
        found_names = self.extract_names_from_transaction_text(text)
        
        # Verificar si el usuario aparece como receptor o emisor
        user_is_recipient = False
        user_is_sender = False
        
        for name in found_names:
            if self.is_user_match(name, user_name):
                # Analizar contexto donde aparece el nombre
                if any(pattern in text_lower for pattern in [
                    'transferencia sinpe móvil a', 'transferencia sinpe movil a', 
                    'sinpe móvil a', 'sinpe movil a', 'sinpe a', 'a ' + name.lower(),
                    'destinatario:', 'receptor:', 'para:', 'recibiste', 'cobro'
                ]):
                    user_is_recipient = True
                
                if any(pattern in text_lower for pattern in [
                    'transferencia sinpe móvil de', 'transferencia sinpe movil de',
                    'sinpe móvil de', 'sinpe movil de', 'sinpe de', 'de ' + name.lower(),
                    'remitente:', 'emisor:', 'desde:', 'enviaste', 'pagaste'
                ]):
                    user_is_sender = True
        
        # Patrones adicionales para determinar dirección
        income_patterns = [
            'recibiste', 'se acreditó', 'se depositó', 'ingreso', 'cobro',
            'transferencia recibida', 'pago recibido'
        ]
        
        expense_patterns = [
            'enviaste', 'pagaste', 'se debitó', 'se descontó', 'gasto',
            'transferencia enviada', 'pago realizado', 'compra'
        ]
        
        has_income_indicators = any(pattern in text_lower for pattern in income_patterns)
        has_expense_indicators = any(pattern in text_lower for pattern in expense_patterns)
        
        # Determinar tipo de transacción
        transaction_type = None
        confidence = 0.0
        reasoning = []
        
        if user_is_recipient and not user_is_sender:
            transaction_type = "ingreso"
            confidence = 0.9
            reasoning.append("Usuario aparece como receptor")
        elif user_is_sender and not user_is_recipient:
            transaction_type = "gasto"
            confidence = 0.9
            reasoning.append("Usuario aparece como emisor")
        elif has_income_indicators and not has_expense_indicators:
            transaction_type = "ingreso"
            confidence = 0.7
            reasoning.append("Indicadores de ingreso encontrados")
        elif has_expense_indicators and not has_income_indicators:
            transaction_type = "gasto"
            confidence = 0.7
            reasoning.append("Indicadores de gasto encontrados")
        else:
            # Análisis por defecto para SINPE con lógica corregida y flexible
            if 'sinpe' in text_lower:
                # Verificar si el usuario es receptor usando patrón flexible
                user_normalized = self.normalize_name(user_name)
                user_parts = user_normalized.split()
                
                # Buscar patrones donde el usuario es receptor (a/para usuario)
                is_user_recipient = False
                is_user_sender = False
                
                # Patrones para receptor: buscar patrones flexibles donde el usuario es destinatario
                recipient_patterns = [
                    'transferencia a ', 'sinpe móvil a ', 'sinpe movil a ', 'sinpe a ',
                    'realizo a ', 'realizó a ', 'envió a ', 'envio a ', 'para '
                ]
                for pattern_prefix in recipient_patterns:
                    pattern_start = text_lower.find(pattern_prefix)
                    if pattern_start >= 0:
                        # Extraer texto después del patrón (hasta 200 caracteres)
                        text_after_pattern = text_lower[pattern_start + len(pattern_prefix):pattern_start + len(pattern_prefix) + 200]
                        # Verificar si contiene todas las partes del nombre del usuario
                        if all(part in text_after_pattern for part in user_parts):
                            is_user_recipient = True
                            break
                
                # Patrones para emisor: "transferencia de [nombre]", "sinpe de [nombre]"
                for pattern_prefix in ['transferencia de ', 'sinpe móvil de ', 'sinpe movil de ', 'sinpe de ']:
                    pattern_start = text_lower.find(pattern_prefix)
                    if pattern_start >= 0:
                        text_after_pattern = text_lower[pattern_start + len(pattern_prefix):]
                        if all(part in text_after_pattern for part in user_parts):
                            is_user_sender = True
                            break
                
                # Determinar tipo basado en análisis flexible
                if is_user_recipient and not is_user_sender:
                    transaction_type = "ingreso"
                    confidence = 0.9
                    reasoning.append("SINPE dirigido específicamente al usuario (INGRESO CONFIRMADO)")
                elif is_user_sender and not is_user_recipient:
                    transaction_type = "gasto"
                    confidence = 0.9
                    reasoning.append("SINPE enviado específicamente por el usuario (GASTO CONFIRMADO)")
                # Patrones genéricos (fallback)
                elif any(pattern in text_lower for pattern in ['transferencia a', 'sinpe móvil a', 'sinpe movil a']):
                    transaction_type = "ingreso"
                    confidence = 0.7
                    reasoning.append("SINPE dirigido a alguien (probablemente ingreso)")
                elif any(pattern in text_lower for pattern in ['transferencia de', 'sinpe móvil de', 'sinpe movil de']):
                    transaction_type = "gasto"
                    confidence = 0.7
                    reasoning.append("SINPE enviado desde alguien (probablemente gasto)")
                else:
                    transaction_type = "gasto"
                    confidence = 0.5
                    reasoning.append("SINPE sin dirección clara")
        
        return {
            'type': transaction_type,
            'confidence': confidence,
            'reasoning': reasoning,
            'found_names': found_names,
            'user_is_recipient': user_is_recipient,
            'user_is_sender': user_is_sender
        }


# Instancia global
name_matcher = NameMatcher()