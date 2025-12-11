#!/usr/bin/env python3
"""Create Turkish translations"""

import json

# Turkish translations
turkish_translations = {
  "common": {
    "save": "Kaydet",
    "cancel": "İptal",
    "delete": "Sil",
    "edit": "Düzenle",
    "add": "Ekle",
    "create": "Oluştur",
    "update": "Güncelle",
    "search": "Ara",
    "filter": "Filtrele",
    "export": "Dışa Aktar",
    "import": "İçe Aktar",
    "loading": "Yükleniyor...",
    "error": "Hata",
    "success": "Başarılı",
    "confirm": "Onayla",
    "yes": "Evet",
    "no": "Hayır",
    "close": "Kapat",
    "back": "Geri",
    "next": "İleri",
    "previous": "Önceki",
    "submit": "Gönder",
    "reset": "Sıfırla",
    "clear": "Temizle",
    "select": "Seç",
    "all": "Tümü",
    "none": "Hiçbiri",
    "active": "Aktif",
    "inactive": "Pasif",
    "status": "Durum",
    "actions": "İşlemler",
    "details": "Detaylar",
    "view": "Görüntüle",
    "download": "İndir",
    "upload": "Yükle",
    "refresh": "Yenile",
    "print": "Yazdır"
  },
  "navigation": {
    "dashboard": "Kontrol Paneli",
    "dashboardDescription": "Sistem metrikleri ve durum özeti",
    "organizations": "Organizasyonlar",
    "organizationsDescription": "Organizasyon hiyerarşisi ve ilişkilerini yönet",
    "organizationManagement": "Organizasyon Yönetimi",
    "organizationManagementDescription": "Gelişmiş organizasyon, tedarikçi ve depo yönetimi",
    "parts": "Parçalar",
    "partsDescription": "Parça kataloğuna göz at ve yönet",
    "orders": "Siparişler",
    "ordersDescription": "Parça siparişleri oluştur ve takip et",
    "stocktake": "Envanter Sayımı",
    "stocktakeDescription": "Envanter düzeltmeleri ve sayımları gerçekleştir",
    "stockAdjustments": "Stok Düzeltmeleri",
    "stockAdjustmentsDescription": "Envanter düzeltmelerini kaydet ve takip et",
    "maintenanceProtocols": "Bakım Protokolleri",
    "maintenanceProtocolsDescription": "Bakım protokol şablonlarını yönet",
    "maintenance": "Bakım",
    "maintenanceDescription": "Bakım gerçekleştir ve takip et",
    "machines": "Makineler",
    "machinesDescription": "AutoBoss makinelerini görüntüle ve yönet",
    "users": "Kullanıcılar",
    "usersDescription": "Kullanıcıları ve izinleri yönet",
    "warehouses": "Depolar",
    "warehousesDescription": "Depo konumlarını ve ayarlarını yönet",
    "transactions": "İşlemler",
    "transactionsDescription": "İşlem geçmişini görüntüle ve yönet",
    "configuration": "Yapılandırma",
    "configurationDescription": "Yönetim yapılandırma paneli",
    "inventory": "Envanter",
    "reports": "Raporlar",
    "settings": "Ayarlar",
    "profile": "Profil",
    "security": "Güvenlik Merkezi",
    "logout": "Çıkış",
    "dailyOperations": "Günlük İşlemler",
    "categories": {
      "core": "Temel",
      "inventory": "Envanter",
      "operations": "İşlemler",
      "administration": "Yönetim"
    }
  },
  "auth": {
    "login": "Giriş",
    "logout": "Çıkış",
    "username": "Kullanıcı Adı",
    "password": "Şifre",
    "email": "E-posta",
    "forgotPassword": "Şifremi Unuttum",
    "rememberMe": "Beni Hatırla",
    "signIn": "Giriş Yap",
    "signOut": "Çıkış Yap",
    "signUp": "Kayıt Ol",
    "signInToAccount": "Hesabınıza Giriş Yapın",
    "createAccount": "Hesap Oluştur",
    "alreadyHaveAccount": "Zaten hesabınız var mı?",
    "dontHaveAccount": "Hesabınız yok mu?"
  },
  "users": {
    "title": "Kullanıcılar",
    "addUser": "Kullanıcı Ekle",
    "editUser": "Kullanıcıyı Düzenle",
    "deleteUser": "Kullanıcıyı Sil",
    "userDetails": "Kullanıcı Detayları",
    "name": "Ad",
    "role": "Rol",
    "organization": "Organizasyon",
    "createdAt": "Oluşturulma Tarihi",
    "lastLogin": "Son Giriş"
  },
  "dashboard": {
    "welcomeBack": "Tekrar hoş geldiniz, {{name}}",
    "quickActions": "Hızlı İşlemler",
    "systemStatus": "Sistem Durumu",
    "allSystemsOperational": "Tüm sistemler çalışıyor",
    "activeUsers": "Aktif Kullanıcılar",
    "onlineNow": "Şu anda çevrimiçi",
    "lowStock": "Düşük Stok",
    "needsAttention": "Dikkat gerekiyor",
    "allGood": "Her şey yolunda",
    "outOfStock": "Stokta Yok",
    "critical": "Kritik",
    "allStocked": "Tümü stokta",
    "pendingOrders": "Bekleyen Siparişler",
    "inProgress": "Devam ediyor",
    "noPending": "Bekleyen yok",
    "recentActivity": "Son Aktivite",
    "last24h": "Son 24 saat",
    "warehouses": "Depolar",
    "activeLocations": "Aktif konumlar",
    "attentionRequired": "Dikkat Gerekli",
    "criticalStockAlert": "Kritik Stok Uyarısı",
    "lowStockWarning": "Düşük Stok Uyarısı",
    "pendingInvitations": "Bekleyen Davetler",
    "pendingOrdersOverview": "Bekleyen Siparişler Özeti",
    "lowStockByOrganization": "Organizasyona Göre Düşük Stok",
    "currentStatus": "Mevcut durum",
    "errorLoading": "Kontrol paneli yüklenirken hata"
  },
  "validation": {
    "required": "Bu alan zorunludur",
    "invalidEmail": "Geçersiz e-posta adresi",
    "minLength": "Minimum uzunluk {{min}} karakterdir",
    "maxLength": "Maksimum uzunluk {{max}} karakterdir",
    "invalidFormat": "Geçersiz format"
  },
  "errors": {
    "generic": "Bir hata oluştu. Lütfen tekrar deneyin.",
    "networkError": "Ağ hatası. Lütfen bağlantınızı kontrol edin.",
    "unauthorized": "Bu işlemi gerçekleştirme yetkiniz yok.",
    "notFound": "Kaynak bulunamadı.",
    "serverError": "Sunucu hatası. Lütfen daha sonra tekrar deneyin."
  },
  "dailyOperations": {
    "title": "Hadi Ağları Yıkayalım!",
    "subtitle": "Günlük işlemler iş akışı - Gününüze doğru başlayın ve bitirin",
    "selectMachine": "Makinenizi Seçin",
    "selectMachinePlaceholder": "-- Bir makine seçin --",
    "sessionStatus": "Oturum Durumu",
    "notStarted": "Başlamadı",
    "inProgress": "Devam Ediyor",
    "completed": "Tamamlandı",
    "startDay": "Güne Başla",
    "endDay": "Günü Bitir",
    "noMachines": "Kullanılabilir makine yok",
    "noProtocols": "Yapılandırılmış protokol yok"
  }
}

# Load English file as base
with open('frontend/src/locales/en.json', 'r', encoding='utf-8') as f:
    en_data = json.load(f)

# Update with Turkish translations
for key in turkish_translations:
    en_data[key] = turkish_translations[key]

# Write Turkish file
with open('frontend/src/locales/tr.json', 'w', encoding='utf-8') as f:
    json.dump(en_data, f, ensure_ascii=False, indent=2)

print("✅ Created Turkish translation file")
