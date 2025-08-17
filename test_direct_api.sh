#!/bin/bash

# Test direct WhatsApp Cloud API
TOKEN="EAAKjweoiTSQBPMb9FTMB82tzn9FTYlHjF7k9r9ouQteK3tXDRi0bTFHgB9cGUvq74qhhkdxjQBpdFkLpgpwYHdcwV3AUWmZChROCe9d6rp74LTbJzccIHUYYOXlIZBNkmxQvgKhLZB460LIMRi690xNnPpxeJjF1ZBRkAB3xIlBttpe7NQNiJZB6ZAKwAYMNWDZCM5KV24dujZAwDGqnFBaAmW6YsOhJAfROvxiZAIWGvOmb5DscZD"
PHONE_NUMBER_ID="765691039959515"

curl -X POST "https://graph.facebook.com/v18.0/$PHONE_NUMBER_ID/messages" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messaging_product": "whatsapp",
    "to": "50660052300",
    "type": "text",
    "text": {"body": "Test desde API directa"}
  }'