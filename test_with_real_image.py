"""
Test con imagen PNG real que Gemini puede procesar
"""
import asyncio
import sys
import os
from PIL import Image, ImageDraw, ImageFont
import io

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from handlers.message_handler import message_handler
from core.supabase import supabase

def create_sinpe_image():
    """Crear una imagen PNG que simule una notificación SINPE"""
    # Crear imagen de 400x600 (típico de captura de pantalla móvil)
    img = Image.new('RGB', (400, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Texto de la notificación SINPE
    texts = [
        "Banco de Costa Rica",
        "",
        "Transferencia SINPE Móvil",
        "",
        "Se realizó una transferencia",
        "SINPE Móvil a:",
        "",
        "ANDREI ANTONIO VARELA SOLANO",
        "",
        "Monto: ₡10,000.00 CRC",
        "",
        "Referencia:",
        "2025081715284001625138542",
        "",
        "Motivo: Transferencia SINPE",
        "",
        "Fecha: 17/08/2025 15:28"
    ]
    
    y_position = 50
    for text in texts:
        if text:  # Solo dibujar texto no vacío
            draw.text((20, y_position), text, fill='black')
        y_position += 25
    
    # Convertir a bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()

async def test_with_real_image():
    """Test con imagen PNG real procesable"""
    try:
        print("TEST: Pipeline completo con imagen PNG real SINPE")
        print("=" * 60)
        
        # Usuario real
        test_phone = "50660052300"
        user_context = await supabase.get_user_with_context(test_phone)
        
        # Crear imagen PNG real
        print("Creando imagen PNG simulada de SINPE...")
        image_data = create_sinpe_image()
        print(f"Imagen creada: {len(image_data)} bytes")
        
        # Caption vacío (como típicamente llegan)
        caption = ""
        
        print(f"\nUsuario: {user_context.get('name', 'Unknown')}")
        print(f"Telefono: {user_context.get('whatsapp_number', 'Unknown')}")
        
        print(f"\nPROCESANDO IMAGEN REAL...")
        
        # Usar el pipeline real de WhatsApp Cloud
        result = await message_handler.handle_image(image_data, caption, user_context)
        
        print(f"\nRESULTADO:")
        print(f"Status: {result.get('status')}")
        if result.get('result'):
            result_data = result['result']
            print(f"Tipo: {result_data.get('type')}")
            print(f"Descripcion: {result_data.get('description', '')[:100]}...")
            print(f"Monto: {result_data.get('amount')}")
        
        print("\nRevisa los logs del servidor para detalles criticos del debug")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_with_real_image())