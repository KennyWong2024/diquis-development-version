export interface Timezone {
    value: string;
    label: string;
    offset: string;
}

export const TIMEZONES: Timezone[] = [
    // Centroamérica y Caribe
    { value: 'America/Costa_Rica', label: 'Costa Rica', offset: 'GMT-6' },
    { value: 'America/El_Salvador', label: 'El Salvador', offset: 'GMT-6' },
    { value: 'America/Guatemala', label: 'Guatemala', offset: 'GMT-6' },
    { value: 'America/Honduras', label: 'Honduras', offset: 'GMT-6' },
    { value: 'America/Managua', label: 'Nicaragua', offset: 'GMT-6' },
    { value: 'America/Panama', label: 'Panamá', offset: 'GMT-5' },
    { value: 'America/Santo_Domingo', label: 'República Dominicana', offset: 'GMT-4' },
    { value: 'America/Havana', label: 'Cuba', offset: 'GMT-5' },
    { value: 'America/Puerto_Rico', label: 'Puerto Rico', offset: 'GMT-4' },

    // Norteamérica
    { value: 'America/New_York', label: 'Estados Unidos (Este - NY)', offset: 'GMT-4' },
    { value: 'America/Chicago', label: 'Estados Unidos (Central - Chicago)', offset: 'GMT-5' },
    { value: 'America/Denver', label: 'Estados Unidos (Montaña - Denver)', offset: 'GMT-6' },
    { value: 'America/Los_Angeles', label: 'Estados Unidos (Pacífico - LA)', offset: 'GMT-7' },
    { value: 'America/Anchorage', label: 'Estados Unidos (Alaska)', offset: 'GMT-8' },
    { value: 'America/Mexico_City', label: 'México (CDMX)', offset: 'GMT-6' },
    { value: 'America/Tijuana', label: 'México (Tijuana)', offset: 'GMT-7' },
    { value: 'America/Cancun', label: 'México (Cancún)', offset: 'GMT-5' },
    { value: 'America/Toronto', label: 'Canadá (Toronto)', offset: 'GMT-4' },
    { value: 'America/Vancouver', label: 'Canadá (Vancouver)', offset: 'GMT-7' },

    // Sudamérica
    { value: 'America/Cordoba', label: 'Argentina (Buenos Aires)', offset: 'GMT-3' },
    { value: 'America/La_Paz', label: 'Bolivia', offset: 'GMT-4' },
    { value: 'America/Sao_Paulo', label: 'Brasil (São Paulo)', offset: 'GMT-3' },
    { value: 'America/Santiago', label: 'Chile (Santiago)', offset: 'GMT-4' },
    { value: 'America/Bogota', label: 'Colombia', offset: 'GMT-5' },
    { value: 'America/Guayaquil', label: 'Ecuador', offset: 'GMT-5' },
    { value: 'America/Asuncion', label: 'Paraguay', offset: 'GMT-4' },
    { value: 'America/Lima', label: 'Perú', offset: 'GMT-5' },
    { value: 'America/Montevideo', label: 'Uruguay', offset: 'GMT-3' },
    { value: 'America/Caracas', label: 'Venezuela', offset: 'GMT-4' },

    // Europa
    { value: 'Europe/Madrid', label: 'España (Península)', offset: 'GMT+1' },
    { value: 'Atlantic/Canary', label: 'España (Canarias)', offset: 'GMT' },
    { value: 'Europe/London', label: 'Reino Unido (Londres)', offset: 'GMT' },
    { value: 'Europe/Paris', label: 'Francia (París)', offset: 'GMT+1' },
    { value: 'Europe/Berlin', label: 'Alemania (Berlín)', offset: 'GMT+1' },
    { value: 'Europe/Rome', label: 'Italia (Roma)', offset: 'GMT+1' },
    { value: 'Europe/Zurich', label: 'Suiza (Zúrich)', offset: 'GMT+1' },
    { value: 'Europe/Stockholm', label: 'Suecia (Estocolmo)', offset: 'GMT+1' },
    { value: 'Europe/Oslo', label: 'Noruega (Oslo)', offset: 'GMT+1' },
    { value: 'Europe/Copenhagen', label: 'Dinamarca (Copenhague)', offset: 'GMT+1' },
    { value: 'Europe/Amsterdam', label: 'Países Bajos (Ámsterdam)', offset: 'GMT+1' },
    { value: 'Europe/Moscow', label: 'Rusia (Moscú)', offset: 'GMT+3' },
    { value: 'Europe/Kyiv', label: 'Ucrania (Kiev)', offset: 'GMT+2' },
    { value: 'Europe/Istanbul', label: 'Turquía (Estambul)', offset: 'GMT+3' },

    // Asia & Oceanía
    { value: 'Asia/Tokyo', label: 'Japón (Tokio)', offset: 'GMT+9' },
    { value: 'Asia/Shanghai', label: 'China (Pekín/Shanghái)', offset: 'GMT+8' },
    { value: 'Asia/Kolkata', label: 'India (Nueva Delhi)', offset: 'GMT+5:30' },
    { value: 'Asia/Seoul', label: 'Corea del Sur (Seúl)', offset: 'GMT+9' },
    { value: 'Asia/Singapore', label: 'Singapur', offset: 'GMT+8' },
    { value: 'Asia/Bangkok', label: 'Tailandia (Bangkok)', offset: 'GMT+7' },
    { value: 'Asia/Jakarta', label: 'Indonesia (Yakarta)', offset: 'GMT+7' },
    { value: 'Australia/Sydney', label: 'Australia (Sídney)', offset: 'GMT+10' },
    { value: 'Australia/Perth', label: 'Australia (Perth)', offset: 'GMT+8' },
    { value: 'Pacific/Auckland', label: 'Nueva Zelanda (Auckland)', offset: 'GMT+12' },

    // Medio Oriente y África
    { value: 'Asia/Dubai', label: 'Emiratos Árabes Unidos (Dubái)', offset: 'GMT+4' },
    { value: 'Asia/Riyadh', label: 'Arabia Saudita (Riad)', offset: 'GMT+3' },
    { value: 'Asia/Jerusalem', label: 'Israel (Jerusalén)', offset: 'GMT+2' },
    { value: 'Africa/Cairo', label: 'Egipto (El Cairo)', offset: 'GMT+2' },
    { value: 'Africa/Johannesburg', label: 'Sudáfrica (Johannesburgo)', offset: 'GMT+2' },
    { value: 'Africa/Lagos', label: 'Nigeria (Lagos)', offset: 'GMT+1' },
    { value: 'Africa/Casablanca', label: 'Marruecos (Casablanca)', offset: 'GMT+1' },

    { value: 'Etc/UTC', label: 'Tiempo Universal Coordinado (UTC)', offset: 'UTC' }
].sort((a, b) => a.label.localeCompare(b.label));