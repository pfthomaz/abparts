#!/usr/bin/env python3
"""
Add PWA translations to all locale files
"""

import json
import os

# Define translations for all languages
translations = {
    'ar': {
        "pwa": {
            "offline": {
                "noConnection": "أنت غير متصل بالإنترنت",
                "withQueue": "غير متصل - {{count}} رسائل في قائمة الانتظار",
                "queued": "في قائمة الانتظار",
                "messageQueued": "تم وضع رسالتك في قائمة الانتظار وسيتم إرسالها عند عودة الاتصال."
            },
            "connection": {
                "poor": "اتصال ضعيف - قد تتأخر الرسائل",
                "moderate": "اتصال متوسط",
                "good": "اتصال جيد",
                "timeout": "انتهت مهلة الطلب. يرجى التحقق من اتصالك والمحاولة مرة أخرى."
            },
            "install": {
                "title": "تثبيت ABParts",
                "description": "قم بتثبيت ABParts على جهازك للوصول الأسرع والقدرات دون اتصال.",
                "install": "تثبيت",
                "later": "لاحقاً"
            },
            "update": {
                "title": "تحديث متاح",
                "description": "يتوفر إصدار جديد من ABParts. أعد التحميل للتحديث.",
                "reload": "إعادة التحميل الآن"
            }
        },
        "aiAssistant": {
            "notifications": {
                "newMessage": "رسالة جديدة من مساعد الذكاء الاصطناعي"
            }
        }
    },
    'el': {
        "pwa": {
            "offline": {
                "noConnection": "Είστε εκτός σύνδεσης",
                "withQueue": "Εκτός σύνδεσης - {{count}} μηνύματα σε αναμονή",
                "queued": "σε αναμονή",
                "messageQueued": "Το μήνυμά σας έχει τεθεί σε ουρά και θα σταλεί όταν επανέλθετε σε σύνδεση."
            },
            "connection": {
                "poor": "Κακή σύνδεση - τα μηνύματα μπορεί να καθυστερήσουν",
                "moderate": "Μέτρια σύνδεση",
                "good": "Καλή σύνδεση",
                "timeout": "Λήξη χρονικού ορίου αιτήματος. Ελέγξτε τη σύνδεσή σας και δοκιμάστε ξανά."
            },
            "install": {
                "title": "Εγκατάσταση ABParts",
                "description": "Εγκαταστήστε το ABParts στη συσκευή σας για ταχύτερη πρόσβαση και δυνατότητες εκτός σύνδεσης.",
                "install": "Εγκατάσταση",
                "later": "Αργότερα"
            },
            "update": {
                "title": "Διαθέσιμη Ενημέρωση",
                "description": "Μια νέα έκδοση του ABParts είναι διαθέσιμη. Επαναφορτώστε για ενημέρωση.",
                "reload": "Επαναφόρτωση Τώρα"
            }
        },
        "aiAssistant": {
            "notifications": {
                "newMessage": "Νέο Μήνυμα Βοηθού AI"
            }
        }
    },
    'es': {
        "pwa": {
            "offline": {
                "noConnection": "Estás desconectado",
                "withQueue": "Desconectado - {{count}} mensajes en cola",
                "queued": "en cola",
                "messageQueued": "Tu mensaje ha sido puesto en cola y se enviará cuando vuelvas a estar en línea."
            },
            "connection": {
                "poor": "Conexión deficiente - los mensajes pueden retrasarse",
                "moderate": "Conexión moderada",
                "good": "Buena conexión",
                "timeout": "Tiempo de espera agotado. Por favor, verifica tu conexión e inténtalo de nuevo."
            },
            "install": {
                "title": "Instalar ABParts",
                "description": "Instala ABParts en tu dispositivo para un acceso más rápido y capacidades sin conexión.",
                "install": "Instalar",
                "later": "Más tarde"
            },
            "update": {
                "title": "Actualización Disponible",
                "description": "Una nueva versión de ABParts está disponible. Recarga para actualizar.",
                "reload": "Recargar Ahora"
            }
        },
        "aiAssistant": {
            "notifications": {
                "newMessage": "Nuevo Mensaje del Asistente AI"
            }
        }
    },
    'no': {
        "pwa": {
            "offline": {
                "noConnection": "Du er frakoblet",
                "withQueue": "Frakoblet - {{count}} meldinger i kø",
                "queued": "i kø",
                "messageQueued": "Meldingen din er satt i kø og vil bli sendt når du er tilbake på nett."
            },
            "connection": {
                "poor": "Dårlig tilkobling - meldinger kan bli forsinket",
                "moderate": "Moderat tilkobling",
                "good": "God tilkobling",
                "timeout": "Forespørsel tidsavbrutt. Vennligst sjekk tilkoblingen din og prøv igjen."
            },
            "install": {
                "title": "Installer ABParts",
                "description": "Installer ABParts på enheten din for raskere tilgang og frakoblede funksjoner.",
                "install": "Installer",
                "later": "Senere"
            },
            "update": {
                "title": "Oppdatering Tilgjengelig",
                "description": "En ny versjon av ABParts er tilgjengelig. Last inn på nytt for å oppdatere.",
                "reload": "Last Inn På Nytt Nå"
            }
        },
        "aiAssistant": {
            "notifications": {
                "newMessage": "Ny AI-assistentmelding"
            }
        }
    },
    'tr': {
        "pwa": {
            "offline": {
                "noConnection": "Çevrimdışısınız",
                "withQueue": "Çevrimdışı - {{count}} mesaj kuyrukta",
                "queued": "kuyrukta",
                "messageQueued": "Mesajınız kuyruğa alındı ve tekrar çevrimiçi olduğunuzda gönderilecek."
            },
            "connection": {
                "poor": "Zayıf bağlantı - mesajlar gecikebilir",
                "moderate": "Orta düzey bağlantı",
                "good": "İyi bağlantı",
                "timeout": "İstek zaman aşımına uğradı. Lütfen bağlantınızı kontrol edin ve tekrar deneyin."
            },
            "install": {
                "title": "ABParts'ı Yükle",
                "description": "Daha hızlı erişim ve çevrimdışı özellikler için ABParts'ı cihazınıza yükleyin.",
                "install": "Yükle",
                "later": "Daha Sonra"
            },
            "update": {
                "title": "Güncelleme Mevcut",
                "description": "ABParts'ın yeni bir sürümü mevcut. Güncellemek için yeniden yükleyin.",
                "reload": "Şimdi Yeniden Yükle"
            }
        },
        "aiAssistant": {
            "notifications": {
                "newMessage": "Yeni AI Asistan Mesajı"
            }
        }
    }
}

def add_translations_to_file(filepath, lang_code):
    """Add PWA translations to a locale file"""
    try:
        # Read existing translations
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Add PWA translations if not already present
        if 'pwa' not in data:
            data['pwa'] = translations[lang_code]['pwa']
            print(f"✓ Added PWA translations to {lang_code}")
        else:
            print(f"⚠ PWA translations already exist in {lang_code}")
        
        # Add aiAssistant.notifications if not present
        if 'aiAssistant' in data:
            if 'notifications' not in data['aiAssistant']:
                data['aiAssistant']['notifications'] = translations[lang_code]['aiAssistant']['notifications']
                print(f"✓ Added AI Assistant notifications to {lang_code}")
            else:
                print(f"⚠ AI Assistant notifications already exist in {lang_code}")
        
        # Write back to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"✗ Error processing {filepath}: {e}")
        return False

def main():
    """Main function to add translations to all locale files"""
    locale_dir = 'frontend/src/locales'
    
    # Skip English as it's already done
    languages = ['ar', 'el', 'es', 'no', 'tr']
    
    print("Adding PWA translations to locale files...")
    print("=" * 60)
    
    success_count = 0
    for lang in languages:
        filepath = os.path.join(locale_dir, f'{lang}.json')
        if os.path.exists(filepath):
            if add_translations_to_file(filepath, lang):
                success_count += 1
        else:
            print(f"✗ File not found: {filepath}")
    
    print("=" * 60)
    print(f"Completed: {success_count}/{len(languages)} files updated successfully")

if __name__ == '__main__':
    main()
