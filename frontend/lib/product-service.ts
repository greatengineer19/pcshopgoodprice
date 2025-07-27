import type {
    ShopContentListWrapper,
    ProductBrand,
    ShopContentProduct,
    ProductFilter
} from "@/types/product"
import { useToastError } from "@/hooks/use-toast-error"
import { handleApiError } from "@/utils/api/error-handlers"
import { toast } from "sonner"
import { ProductCategory } from "@/types/computer-component-category"
const SECRET_KEY_NAME = 'secret_key';

export const fetchProducts = async (filters?: ProductFilter): Promise<{ result: ShopContentListWrapper }> => {
    let token: string | null = null;
    if (typeof window !== "undefined") {
        token = localStorage.getItem(SECRET_KEY_NAME);
    }
    let queryString = ''

    if (filters) {
        const query_params = {
            component_category_ids: filters.categories?.length ? filters.categories.map(c => c.id).join(',') : '',
            start_price: filters.priceRange ? String(filters.priceRange[0]) : '',
            end_price: filters.priceRange ? String(filters.priceRange[1]) : '',
            min_rating: filters.ratings ? String(filters.ratings) : ''
        }

        queryString = '?' + new URLSearchParams(query_params).toString();
    }
    
    let response = await fetch("http://localhost:8000/api/sellable-products" + queryString, {
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        }
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || "Failed to fetch products");
    }
    
    const responseData = await response.json();
    const products: ShopContentListWrapper = responseData;

    return {
        result: products
    }
}

// Fetch product by slug
export const fetchProductBySlug = async (slug: string): Promise<ShopContentProduct> => {
    let token: string | null = null;
    if (typeof window !== "undefined") {
        token = localStorage.getItem(SECRET_KEY_NAME);
    }
    let response = await fetch("http://localhost:8000/api/sellable-products/" + slug, {
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        }
    });

    if (!response.ok) {
        throw new Error("Failed to fetch products");
    }
    
    const responseData = await response.json();
    const product: ShopContentProduct = responseData;

    return product
}

// Fetch product categories
export const fetchProductCategories = async (): Promise<ProductCategory[]> => {
    let response = await fetch("http://localhost:8000/api/computer-component-categories");

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || "Failed to fetch categories");
    }
    
    const responseData = await response.json();
    const categories: ProductCategory[] = responseData.computer_component_categories;

    return categories
}

// Fetch product brands
export const fetchProductBrands = async (): Promise<ProductBrand[]> => {
    return [];
    const response = await fetch('http://localhost:8000/api/product-brands');

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || "Failed to fetch product brands");
    }

    const responseData = await response.json();
    const productBrands: ProductBrand[] = responseData.product_brands;

    return productBrands
}