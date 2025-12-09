#!/usr/bin/env python3
"""Add User Form translations to all locale files."""

import json

# Translation mappings for all languages
translations = {
    "en": {
        "username": "Username",
        "password": "Password",
        "passwordKeepCurrent": "(Leave blank to keep current)",
        "preferredLanguage": "Preferred Language",
        "userStatus": "User Status",
        "active": "Active",
        "submitting": "Submitting...",
        "updateUser": "Update User",
        "createUser": "Create User",
        "unexpectedError": "An unexpected error occurred."
    },
    "el": {  # Greek
        "username": "Όνομα Χρήστη",
        "password": "Κωδικός Πρόσβασης",
        "passwordKeepCurrent": "(Αφήστε κενό για να διατηρήσετε τον τρέχοντα)",
        "preferredLanguage": "Προτιμώμενη Γλώσσα",
        "userStatus": "Κατάσταση Χρήστη",
        "active": "Ενεργός",
        "submitting": "Υποβολή...",
        "updateUser": "Ενημέρωση Χρήστη",
        "createUser": "Δημιουργία Χρήστη",
        "unexpectedError": "Προέκυψε ένα απροσδόκητο σφάλμα."
    },
    "ar": {  # Arabic
        "username": "اسم المستخدم",
        "password": "كلمة المرور",
        "passwordKeepCurrent": "(اتركه فارغًا للاحتفاظ بالحالي)",
        "preferredLanguage": "اللغة المفضلة",
        "userStatus": "حالة المستخدم",
        "active": "نشط",
        "submitting": "جارٍ الإرسال...",
        "updateUser": "تحديث المستخدم",
        "createUser": "إنشاء مستخدم",
        "unexpectedError": "حدث خطأ غير متوقع."
    },
    "es": {  # Spanish
        "username": "Nombre de Usuario",
        "password": "Contraseña",
        "passwordKeepCurrent": "(Dejar en blanco para mantener actual)",
        "preferredLanguage": "Idioma Preferido",
        "userStatus": "Estado del Usuario",
        "active": "Activo",
        "submitting": "Enviando...",
        "updateUser": "Actualizar Usuario",
        "createUser": "Crear Usuario",
        "unexpectedError": "Ocurrió un error inesperado."
    },
    "tr": {  # Turkish
        "username": "Kullanıcı Adı",
        "password": "Şifre",
        "passwordKeepCurrent": "(Mevcut şifreyi korumak için boş bırakın)",
        "preferredLanguage": "Tercih Edilen Dil",
        "userStatus": "Kullanıcı Durumu",
        "active": "Aktif",
        "submitting": "Gönderiliyor...",
        "updateUser": "Kullanıcıyı Güncelle",
        "createUser": "Kullanıcı Oluştur",
        "unexpectedError": "Beklenmeyen bir hata oluştu."
    },
    "no": {  # Norwegian
        "username": "Brukernavn",
        "password": "Passord",
        "passwordKeepCurrent": "(La stå tomt for å beholde nåværende)",
        "preferredLanguage": "Foretrukket Språk",
        "userStatus": "Brukerstatus",
        "active": "Aktiv",
        "submitting": "Sender...",
        "updateUser": "Oppdater Bruker",
        "createUser": "Opprett Bruker",
        "unexpectedError": "En uventet feil oppstod."
    }
}

def add_translations_to_file(lang_code, translations_dict):
    """Add translations to a specific language file."""
    file_path = f"frontend/src/locales/{lang_code}.json"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Add userForm section
        data["userForm"] = translations_dict
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Updated {lang_code}.json with {len(translations_dict)} keys")
        
    except Exception as e:
        print(f"❌ Error updating {lang_code}.json: {e}")

# Process all languages
for lang_code, trans in translations.items():
    add_translations_to_file(lang_code, trans)

print("\n✅ All User Form translations added successfully!")
print(f"📊 Total keys per language: {len(translations['en'])}")
