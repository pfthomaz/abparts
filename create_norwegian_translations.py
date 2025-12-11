#!/usr/bin/env python3
"""Create Norwegian translations"""

import json

# Norwegian translations
norwegian_translations = {
  "common": {
    "save": "Lagre",
    "cancel": "Avbryt",
    "delete": "Slett",
    "edit": "Rediger",
    "add": "Legg til",
    "create": "Opprett",
    "update": "Oppdater",
    "search": "Søk",
    "filter": "Filtrer",
    "export": "Eksporter",
    "import": "Importer",
    "loading": "Laster...",
    "error": "Feil",
    "success": "Suksess",
    "confirm": "Bekreft",
    "yes": "Ja",
    "no": "Nei",
    "close": "Lukk",
    "back": "Tilbake",
    "next": "Neste",
    "previous": "Forrige",
    "submit": "Send inn",
    "reset": "Tilbakestill",
    "clear": "Tøm",
    "select": "Velg",
    "all": "Alle",
    "none": "Ingen",
    "active": "Aktiv",
    "inactive": "Inaktiv",
    "status": "Status",
    "actions": "Handlinger",
    "details": "Detaljer",
    "view": "Vis",
    "download": "Last ned",
    "upload": "Last opp",
    "refresh": "Oppdater",
    "print": "Skriv ut"
  },
  "navigation": {
    "dashboard": "Dashbord",
    "dashboardDescription": "Oversikt over systemmetrikker og status",
    "organizations": "Organisasjoner",
    "organizationsDescription": "Administrer organisasjonshierarki og relasjoner",
    "organizationManagement": "Organisasjonsstyring",
    "organizationManagementDescription": "Forbedret organisasjons-, leverandør- og lagerstyring",
    "parts": "Deler",
    "partsDescription": "Bla gjennom og administrer delekatalog",
    "orders": "Bestillinger",
    "ordersDescription": "Opprett og spor delebestillinger",
    "stocktake": "Varetelling",
    "stocktakeDescription": "Utfør lagerjusteringer og varetellinger",
    "stockAdjustments": "Lagerjusteringer",
    "stockAdjustmentsDescription": "Registrer og spor lagerjusteringer",
    "maintenanceProtocols": "Vedlikeholdsprotokoller",
    "maintenanceProtocolsDescription": "Administrer vedlikeholdsprotokollmaler",
    "maintenance": "Vedlikehold",
    "maintenanceDescription": "Utfør og spor vedlikehold",
    "machines": "Maskiner",
    "machinesDescription": "Vis og administrer AutoBoss-maskiner",
    "users": "Brukere",
    "usersDescription": "Administrer brukere og tillatelser",
    "warehouses": "Lagre",
    "warehousesDescription": "Administrer lagerlokasjoner og innstillinger",
    "transactions": "Transaksjoner",
    "transactionsDescription": "Vis og administrer transaksjonshistorikk",
    "configuration": "Konfigurasjon",
    "configurationDescription": "Administrativt konfigurasjonspanel",
    "inventory": "Beholdning",
    "reports": "Rapporter",
    "settings": "Innstillinger",
    "profile": "Profil",
    "security": "Sikkerhetssenter",
    "logout": "Logg ut",
    "dailyOperations": "Daglige Operasjoner",
    "categories": {
      "core": "Kjerne",
      "inventory": "Beholdning",
      "operations": "Operasjoner",
      "administration": "Administrasjon"
    }
  },
  "auth": {
    "login": "Logg inn",
    "logout": "Logg ut",
    "username": "Brukernavn",
    "password": "Passord",
    "email": "E-post",
    "forgotPassword": "Glemt passord",
    "rememberMe": "Husk meg",
    "signIn": "Logg inn",
    "signOut": "Logg ut",
    "signUp": "Registrer deg",
    "signInToAccount": "Logg inn på kontoen din",
    "createAccount": "Opprett konto",
    "alreadyHaveAccount": "Har du allerede en konto?",
    "dontHaveAccount": "Har du ikke en konto?"
  },
  "users": {
    "title": "Brukere",
    "addUser": "Legg til bruker",
    "editUser": "Rediger bruker",
    "deleteUser": "Slett bruker",
    "userDetails": "Brukerdetaljer",
    "name": "Navn",
    "role": "Rolle",
    "organization": "Organisasjon",
    "createdAt": "Opprettet",
    "lastLogin": "Siste innlogging"
  },
  "dashboard": {
    "welcomeBack": "Velkommen tilbake, {{name}}",
    "quickActions": "Hurtighandlinger",
    "systemStatus": "Systemstatus",
    "allSystemsOperational": "Alle systemer operative",
    "activeUsers": "Aktive brukere",
    "onlineNow": "Online nå",
    "lowStock": "Lavt lager",
    "needsAttention": "Trenger oppmerksomhet",
    "allGood": "Alt bra",
    "outOfStock": "Utsolgt",
    "critical": "Kritisk",
    "allStocked": "Alt på lager",
    "pendingOrders": "Ventende bestillinger",
    "inProgress": "Pågår",
    "noPending": "Ingen ventende",
    "recentActivity": "Nylig aktivitet",
    "last24h": "Siste 24t",
    "warehouses": "Lagre",
    "activeLocations": "Aktive lokasjoner",
    "attentionRequired": "Oppmerksomhet påkrevd",
    "criticalStockAlert": "Kritisk lagervarsel",
    "lowStockWarning": "Lavt lagervarsel",
    "pendingInvitations": "Ventende invitasjoner",
    "pendingOrdersOverview": "Oversikt over ventende bestillinger",
    "lowStockByOrganization": "Lavt lager etter organisasjon",
    "currentStatus": "Nåværende status",
    "errorLoading": "Feil ved lasting av dashbord"
  },
  "validation": {
    "required": "Dette feltet er påkrevd",
    "invalidEmail": "Ugyldig e-postadresse",
    "minLength": "Minimum lengde er {{min}} tegn",
    "maxLength": "Maksimal lengde er {{max}} tegn",
    "invalidFormat": "Ugyldig format"
  },
  "errors": {
    "generic": "En feil oppstod. Vennligst prøv igjen.",
    "networkError": "Nettverksfeil. Vennligst sjekk tilkoblingen din.",
    "unauthorized": "Du har ikke tillatelse til å utføre denne handlingen.",
    "notFound": "Ressurs ikke funnet.",
    "serverError": "Serverfeil. Vennligst prøv igjen senere."
  },
  "dailyOperations": {
    "title": "La oss vaske nett!",
    "subtitle": "Daglig driftsarbeidsflyt - Start og avslutt dagen riktig",
    "selectMachine": "Velg maskinen din",
    "selectMachinePlaceholder": "-- Velg en maskin --",
    "sessionStatus": "Øktstatus",
    "notStarted": "Ikke startet",
    "inProgress": "Pågår",
    "completed": "Fullført",
    "startDay": "Start dagen",
    "endDay": "Avslutt dagen",
    "noMachines": "Ingen tilgjengelige maskiner",
    "noProtocols": "Ingen konfigurerte protokoller"
  }
}

# Load English file as base
with open('frontend/src/locales/en.json', 'r', encoding='utf-8') as f:
    en_data = json.load(f)

# Update with Norwegian translations
for key in norwegian_translations:
    en_data[key] = norwegian_translations[key]

# Write Norwegian file
with open('frontend/src/locales/no.json', 'w', encoding='utf-8') as f:
    json.dump(en_data, f, ensure_ascii=False, indent=2)

print("✅ Created Norwegian translation file")
