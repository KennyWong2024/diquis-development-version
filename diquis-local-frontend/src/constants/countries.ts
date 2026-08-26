export interface Country {
    code: string;
    name: string;
}

export const COUNTRIES: Country[] = [
    // Centroamérica y Caribe
    { code: 'cr', name: 'Costa Rica' },
    { code: 'do', name: 'República Dominicana' },
    { code: 'gt', name: 'Guatemala' },
    { code: 'hn', name: 'Honduras' },
    { code: 'ni', name: 'Nicaragua' },
    { code: 'pa', name: 'Panamá' },
    { code: 'sv', name: 'El Salvador' },

    // Norteamérica
    { code: 'ca', name: 'Canadá' },
    { code: 'mx', name: 'México' },
    { code: 'us', name: 'Estados Unidos' },

    // Sudamérica
    { code: 'ar', name: 'Argentina' },
    { code: 'bo', name: 'Bolivia' },
    { code: 'br', name: 'Brasil' },
    { code: 'cl', name: 'Chile' },
    { code: 'co', name: 'Colombia' },
    { code: 'pe', name: 'Perú' },
    { code: 'py', name: 'Paraguay' },
    { code: 'uy', name: 'Uruguay' },
    { code: 've', name: 'Venezuela' },

    // Europa
    { code: 'ch', name: 'Suiza' },
    { code: 'dk', name: 'Dinamarca' },
    { code: 'es', name: 'España' },
    { code: 'eu', name: 'Unión Europea' },
    { code: 'gb', name: 'Reino Unido' },
    { code: 'no', name: 'Noruega' },
    { code: 'se', name: 'Suecia' },

    // Asia & Oceanía
    { code: 'au', name: 'Australia' },
    { code: 'cn', name: 'China' },
    { code: 'in', name: 'India' },
    { code: 'jp', name: 'Japón' },
    { code: 'kr', name: 'Corea del Sur' },
    { code: 'nz', name: 'Nueva Zelanda' },
    { code: 'sg', name: 'Singapur' },

    // Medio Oriente y África
    { code: 'ae', name: 'Emiratos Árabes Unidos' },
    { code: 'il', name: 'Israel' },
    { code: 'za', name: 'Sudáfrica' }
].sort((a, b) => a.name.localeCompare(b.name));