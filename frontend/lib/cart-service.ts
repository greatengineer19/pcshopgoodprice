import type { CartLine, PaymentMethod } from "@/types/cart"
import { useToastSuccess } from "@/hooks/use-toast-success"

const { showSuccessToast } = useToastSuccess()
const SECRET_KEY_NAME = 'secret_key';

// Payment methods
export const listPaymentMethods = async (): Promise<PaymentMethod[]> => {
    const response = await fetch('http://localhost:80/api/cart/payment-methods');
    
    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || "Failed to fetch payment methods");
    }

    const responseData = await response.json();
    const paymentMethods: PaymentMethod[] = responseData.payment_methods;

    return paymentMethods
}

// Fetch cart
export const fetchCart = async (): Promise<CartLine[]> => {
    let token: string | null = null;
    if (typeof window !== "undefined") {
        token = localStorage.getItem(SECRET_KEY_NAME);
    }

    const response = await fetch('http://localhost:80/api/cart', {
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        }
    });
    
    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || "Failed to fetch cart");
    }

    const responseData = await response.json();
    const cartLines: CartLine[] = responseData.cart;

    return cartLines
}

// Add item to cart
export const addToCart = async (productId: number, quantity: number): Promise<string> => {
    let token: string | null = null;
    if (typeof window !== "undefined") {
        token = localStorage.getItem(SECRET_KEY_NAME);
    }

    const payload = {
        id: null,
        component_id: productId,
        quantity: quantity
    };
    
    const response = await fetch("http://localhost:80/api/cart/add-item", {
        method: 'POST',
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(payload),
    });
    
    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || "Failed to fetch product brands");
    }

    return 'ok'
}

// Remove item from cart
export const removeFromCart = async (itemId: number): Promise<string> => {
    let token: string | null = null;
    if (typeof window !== "undefined") {
        token = localStorage.getItem(SECRET_KEY_NAME);
    }

    const response = await fetch(
        "http://localhost:80/api/cart/remove-item/" + itemId,
        {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                "Authorization": `Bearer ${token}`
            },
        });
        

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || "Failed to fetch products");
    }

    showSuccessToast("Product deleted successfully");

    return 'ok'
}