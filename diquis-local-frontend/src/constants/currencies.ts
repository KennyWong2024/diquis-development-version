export interface Currency {
    code: string;
    name: string;
    symbol: string;
    countryCode: string;
}

export const CURRENCIES: Currency[] = [
    // Centroamérica y Caribe
    { code: 'CRC', name: 'Colón Costarricense', symbol: '₡', countryCode: 'cr' },
    { code: 'PAB', name: 'Balboa Panameño', symbol: 'B/.', countryCode: 'pa' },
    { code: 'NIO', name: 'Córdoba Nicaragüense', symbol: 'C$', countryCode: 'ni' },
    { code: 'HNL', name: 'Lempira Hondureño', symbol: 'L', countryCode: 'hn' },
    { code: 'SVC', name: 'Colón Salvadoreño', symbol: '$', countryCode: 'sv' },
    { code: 'GTQ', name: 'Quetzal Guatemalteco', symbol: 'Q', countryCode: 'gt' },
    { code: 'DOP', name: 'Peso Dominicano', symbol: 'RD$', countryCode: 'do' },

    // Norteamérica
    { code: 'USD', name: 'Dólar Estadounidense', symbol: '$', countryCode: 'us' },
    { code: 'MXN', name: 'Peso Mexicano', symbol: '$', countryCode: 'mx' },
    { code: 'CAD', name: 'Dólar Canadiense', symbol: '$', countryCode: 'ca' },

    // Sudamérica
    { code: 'COP', name: 'Peso Colombiano', symbol: '$', countryCode: 'co' },
    { code: 'ARS', name: 'Peso Argentino', symbol: '$', countryCode: 'ar' },
    { code: 'CLP', name: 'Peso Chileno', symbol: '$', countryCode: 'cl' },
    { code: 'PEN', name: 'Sol Peruano', symbol: 'S/', countryCode: 'pe' },
    { code: 'UYU', name: 'Peso Uruguayo', symbol: '$U', countryCode: 'uy' },
    { code: 'BRL', name: 'Real Brasileño', symbol: 'R$', countryCode: 'br' },
    { code: 'BOB', name: 'Boliviano', symbol: 'Bs.', countryCode: 'bo' },
    { code: 'PYG', name: 'Guaraní Paraguayo', symbol: '₲', countryCode: 'py' },
    { code: 'VES', name: 'Bolívar Venezolano', symbol: 'Bs.S', countryCode: 've' },

    // Europa
    { code: 'EUR', name: 'Euro', symbol: '€', countryCode: 'eu' },
    { code: 'GBP', name: 'Libra Esterlina', symbol: '£', countryCode: 'gb' },
    { code: 'CHF', name: 'Franco Suizo', symbol: 'Fr.', countryCode: 'ch' },
    { code: 'SEK', name: 'Corona Sueca', symbol: 'kr', countryCode: 'se' },
    { code: 'NOK', name: 'Corona Noruega', symbol: 'kr', countryCode: 'no' },
    { code: 'DKK', name: 'Corona Danesa', symbol: 'kr', countryCode: 'dk' },

    // Asia & Oceanía
    { code: 'JPY', name: 'Yen Japonés', symbol: '¥', countryCode: 'jp' },
    { code: 'CNY', name: 'Yuan Chino', symbol: '¥', countryCode: 'cn' },
    { code: 'INR', name: 'Rupia India', symbol: '₹', countryCode: 'in' },
    { code: 'AUD', name: 'Dólar Australiano', symbol: '$', countryCode: 'au' },
    { code: 'NZD', name: 'Dólar Neozelandés', symbol: '$', countryCode: 'nz' },
    { code: 'KRW', name: 'Won Surcoreano', symbol: '₩', countryCode: 'kr' },
    { code: 'SGD', name: 'Dólar Singapurense', symbol: '$', countryCode: 'sg' },

    // Medio Oriente y África
    { code: 'AED', name: 'Dírham Emiratí', symbol: 'د.إ', countryCode: 'ae' },
    { code: 'ZAR', name: 'Rand Sudafricano', symbol: 'R', countryCode: 'za' },
    { code: 'ILS', name: 'Nuevo Séquel Israelí', symbol: '₪', countryCode: 'il' }
].sort((a, b) => a.name.localeCompare(b.name));