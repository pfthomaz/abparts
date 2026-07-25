#!/usr/bin/env python3
"""Add User Invitation Form translations to all locale files."""

import json

# Translation mappings for all languages
translations = {
    "en": {
        "title": "Invite New User",
        "subtitle": "Send an invitation email to a new user to join your organization.",
        "emailAddress": "Email Address",
        "emailPlaceholder": "user@example.com",
        "fullName": "Full Name",
        "namePlaceholder": "John Doe",
        "selectOrganization": "Select organization",
        "invitationNote": "The invited user will receive an email with a secure link to set up their account. The invitation will expire after 7 days.",
        "cancel": "Cancel",
        "sendInvitation": "Send Invitation",
        "sendingInvitation": "Sending Invitation...",
        "accessRestricted": "Access Restricted",
        "accessRestrictedMessage": "Only admins and super admins can send user invitations.",
        "error": "Error:",
        "failedToSendInvitation": "Failed to send invitation."
    },
    "el": {  # Greek
        "title": "Πρόσκληση Νέου Χρήστη",
        "subtitle": "Στείλτε email πρόσκλησης σε νέο χρήστη για να συμμετάσχει στον οργανισμό σας.",
        "emailAddress": "Διεύθυνση Email",
        "emailPlaceholder": "χρηστης@παραδειγμα.com",
        "fullName": "Πλήρες Όνομα",
        "namePlaceholder": "Γιάννης Παπαδόπουλος",
        "selectOrganization": "Επιλέξτε οργανισμό",
        "invitationNote": "Ο προσκεκλημένος χρήστης θα λάβει email με ασφαλή σύνδεσμο για να ρυθμίσει τον λογαριασμό του. Η πρόσκληση θα λήξει μετά από 7 ημέρες.",
        "cancel": "Ακύρωση",
        "sendInvitation": "Αποστολή Πρόσκλησης",
        "sendingInvitation": "Αποστολή Πρόσκλησης...",
        "accessRestricted": "Περιορισμένη Πρόσβαση",
        "accessRestrictedMessage": "Μόνο διαχειριστές και υπερ-διαχειριστές μπορούν να στείλουν προσκλήσεις χρηστών.",
        "error": "Σφάλμα:",
        "failedToSendInvitation": "Αποτυχία αποστολής πρόσκλησης."
    },
    "ar": {  # Arabic
        "title": "دعوة مستخدم جديد",
        "subtitle": "أرسل بريدًا إلكترونيًا للدعوة إلى مستخدم جديد للانضمام إلى مؤسستك.",
        "emailAddress": "عنوان البريد الإلكتروني",
        "emailPlaceholder": "user@example.com",
        "fullName": "الاسم الكامل",
        "namePlaceholder": "أحمد محمد",
        "selectOrganization": "اختر المنظمة",
        "invitationNote": "سيتلقى المستخدم المدعو بريدًا إلكترونيًا يحتوي على رابط آمن لإعداد حسابه. ستنتهي صلاحية الدعوة بعد 7 أيام.",
        "cancel": "إلغاء",
        "sendInvitation": "إرسال الدعوة",
        "sendingInvitation": "جارٍ إرسال الدعوة...",
        "accessRestricted": "وصول محدود",
        "accessRestrictedMessage": "يمكن للمسؤولين والمسؤولين الرئيسيين فقط إرسال دعوات المستخدمين.",
        "error": "خطأ:",
        "failedToSendInvitation": "فشل إرسال الدعوة."
    },
    "es": {  # Spanish
        "title": "Invitar Nuevo Usuario",
        "subtitle": "Envía un correo de invitación a un nuevo usuario para unirse a tu organización.",
        "emailAddress": "Dirección de Correo",
        "emailPlaceholder": "usuario@ejemplo.com",
        "fullName": "Nombre Completo",
        "namePlaceholder": "Juan Pérez",
        "selectOrganization": "Seleccionar organización",
        "invitationNote": "El usuario invitado recibirá un correo con un enlace seguro para configurar su cuenta. La invitación expirará después de 7 días.",
        "cancel": "Cancelar",
        "sendInvitation": "Enviar Invitación",
        "sendingInvitation": "Enviando Invitación...",
        "accessRestricted": "Acceso Restringido",
        "accessRestrictedMessage": "Solo los administradores y superadministradores pueden enviar invitaciones de usuario.",
        "error": "Error:",
        "failedToSendInvitation": "Error al enviar invitación."
    },
    "tr": {  # Turkish
        "title": "Yeni Kullanıcı Davet Et",
        "subtitle": "Organizasyonunuza katılması için yeni bir kullanıcıya davet e-postası gönderin.",
        "emailAddress": "E-posta Adresi",
        "emailPlaceholder": "kullanici@ornek.com",
        "fullName": "Tam Ad",
        "namePlaceholder": "Ahmet Yılmaz",
        "selectOrganization": "Organizasyon seçin",
        "invitationNote": "Davet edilen kullanıcı, hesabını kurmak için güvenli bir bağlantı içeren bir e-posta alacaktır. Davet 7 gün sonra sona erecektir.",
        "cancel": "İptal",
        "sendInvitation": "Davet Gönder",
        "sendingInvitation": "Davet Gönderiliyor...",
        "accessRestricted": "Erişim Kısıtlı",
        "accessRestrictedMessage": "Yalnızca yöneticiler ve süper yöneticiler kullanıcı davetleri gönderebilir.",
        "error": "Hata:",
        "failedToSendInvitation": "Davet gönderilemedi."
    },
    "no": {  # Norwegian
        "title": "Inviter Ny Bruker",
        "subtitle": "Send en invitasjons-e-post til en ny bruker for å bli med i organisasjonen din.",
        "emailAddress": "E-postadresse",
        "emailPlaceholder": "bruker@eksempel.com",
        "fullName": "Fullt Navn",
        "namePlaceholder": "Ola Nordmann",
        "selectOrganization": "Velg organisasjon",
        "invitationNote": "Den inviterte brukeren vil motta en e-post med en sikker lenke for å sette opp kontoen sin. Invitasjonen utløper etter 7 dager.",
        "cancel": "Avbryt",
        "sendInvitation": "Send Invitasjon",
        "sendingInvitation": "Sender Invitasjon...",
        "accessRestricted": "Begrenset Tilgang",
        "accessRestrictedMessage": "Bare administratorer og superadministratorer kan sende brukerinvitasjoner.",
        "error": "Feil:",
        "failedToSendInvitation": "Kunne ikke sende invitasjon."
    }
}

def add_translations_to_file(lang_code, translations_dict):
    """Add translations to a specific language file."""
    file_path = f"frontend/src/locales/{lang_code}.json"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Add userInvitation section
        data["userInvitation"] = translations_dict
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Updated {lang_code}.json with {len(translations_dict)} keys")
        
    except Exception as e:
        print(f"❌ Error updating {lang_code}.json: {e}")

# Process all languages
for lang_code, trans in translations.items():
    add_translations_to_file(lang_code, trans)

print("\n✅ All User Invitation Form translations added successfully!")
print(f"📊 Total keys per language: {len(translations['en'])}")
