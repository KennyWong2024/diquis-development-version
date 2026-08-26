import {
    // --- Base / Semilla ---
    ShoppingCart, Car, Utensils, Home, HeartPulse,
    Zap, Briefcase, PiggyBank, MoreHorizontal, Star,
    FileText, Tv, BookOpen, Package, Tag, TrendingDown,
    TrendingUp, ArrowRightLeft,

    // --- Dinero / Finanzas ---
    DollarSign, CreditCard, Coins, Wallet, Receipt, Landmark, Building,

    // --- Comida / Bebida ---
    Coffee, Pizza, Wine, Beer, Apple, CupSoda,

    // --- Compras / Retail ---
    ShoppingBag, Gift, Shirt, Smartphone, Laptop, Scissors, Gem, Watch,

    // --- Transporte / Viajes ---
    Bus, Train, Plane, Ship, Bike, MapPin, Compass, Tent,

    // --- Salud / Deportes / Hobbies ---
    Dumbbell, Activity, Stethoscope, Pill, Syringe,
    Trophy, Medal, Target, Flag,

    // --- Hogar / Familia / Mascotas ---
    Wifi, Droplet, Flame, Wrench, PaintBucket, Trash, Key,
    Baby, PawPrint,

    // --- Entretenimiento / Estilo de vida ---
    Music, Gamepad2, Camera, Ticket, Palmtree, Clapperboard,
    Headphones, Palette, GraduationCap
} from 'lucide-vue-next';

// Diccionario centralizado
export const iconRegistry: Record<string, any> = {
    // Base
    ShoppingCart, Car, Utensils, Home, HeartPulse, Zap, Briefcase, PiggyBank,
    MoreHorizontal, Star, FileText, Tv, BookOpen, Package, Tag, TrendingDown,
    TrendingUp, ArrowRightLeft,

    // Finanzas
    DollarSign, CreditCard, Coins, Wallet, Receipt, Landmark, Building,

    // Comida y Bebida (Proteína/Shakers)
    Coffee, Pizza, Wine, Beer, Apple, CupSoda,

    // Compras y Lujos
    ShoppingBag, Gift, Shirt, Smartphone, Laptop, Scissors, Gem, Watch,

    // Transporte y Aventura
    Bus, Train, Plane, Ship, Bike, MapPin, Compass, Tent,

    // Salud y Deportes (Gym, Canchas, Torneos)
    Dumbbell, Activity, Stethoscope, Pill, Syringe, Trophy, Medal, Target, Flag,

    // Hogar, Familia y Mascotas
    Wifi, Droplet, Flame, Wrench, PaintBucket, Trash, Key, Baby, PawPrint,

    // Entretenimiento, Arte y Educación
    Music, Gamepad2, Camera, Ticket, Palmtree, Clapperboard, Headphones, Palette, GraduationCap
};

export const resolveIcon = (iconName?: string | null) => {
    if (!iconName) return Package;
    return iconRegistry[iconName] || Package;
};


export const getAvailableIconNames = () => {
    return Object.keys(iconRegistry);
};