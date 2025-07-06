export interface ProductBase {
    name: string;
    product_code: string;
    component_category_name: string;
    description: string;
    [key: string]: any;
}

export interface ProductInFrontend extends ProductBase {
    id: number | null;
    image: string | undefined;
    component_category_id: number;
    computer_component_sell_price_settings: DailyProductPrice[];
}

export interface DailyProductPrice {
    id: number | null
    day_type: string
    price_per_unit: number
    active: boolean
}

export interface ProductResponseWithPriceSettings extends ProductBase {
    id: number;
    component_category_name: string;
    component_category_id: number;
    computer_component_sell_price_settings: DailyProductPrice[]
    images?: string[] | null;
}

export interface ProductParams extends ProductBase {
    id: number | null;
    component_category_name: string;
    component_category_id: number | null;
    computer_component_sell_price_settings_attributes: DailyProductPrice[]
    images?: string[] | null;
}

export interface ProductFromBackend extends ProductBase {
    id: number | null;
    images?: string[] | null;
    price: number;
    stock: number;
}

export interface ComputerComponentSellPriceSetting {
    id: number;
    component_id: number;
    day_type: string;
    price_per_unit: string;
    active: boolean;
}

export interface ShopContentProduct {
    rating: number;
    count_review_given: number;
    sell_price: number;
    id: number;
    component_category_id: number;
    component_category_name: string | null;
    computer_component_sell_price_settings: ComputerComponentSellPriceSetting[];
    images: string[] | null;
    created_at: string;
    updated_at: string;
    description: string | null;
    name: string;
    product_code: string;
    price: number;
    status: number;
    stock: number;
    [key: string]: any;
}

export interface ShopContentCategory {
    name: string;
    components: ShopContentProduct[]
}

export interface ShopContentDictionary {
    [key: string]: ShopContentCategory; // key is 0,1,2,3,4
}

export interface ShopContentListWrapper {
    sellable_products: ShopContentDictionary;
    total_item: number;
}

export interface ProductBrand {
    id: number
    name: string
}

export interface ProductFilter {
    categories: string[] | null
    ratings: number | null
    priceRange: number[] | null
}