export interface Category {
    id: string;
    name: string;
    domain: string;
    icon: string | null;
    is_system: boolean;
    is_essential_default: boolean;
    sort_order: number;
}

export interface CategoryCreate {
    name: string;
    domain: string;
    icon?: string | null;
}

export interface CategoryUpdate {
    name?: string;
    icon?: string | null;
}