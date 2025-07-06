import type { CartLine, PaymentMethod } from "@/types/cart"
import { fetchProductBySlug } from "./product-service"
import { handleApiError } from "@/utils/api/error-handlers"
import { toast } from "sonner"
import { useToastError } from "@/hooks/use-toast-error"
import { useToastSuccess } from "@/hooks/use-toast-success"

const { showErrorToast } = useToastError()
const { showSuccessToast } = useToastSuccess()
const SECRET_KEY_NAME = 'secret_key';
const token = localStorage.getItem(SECRET_KEY_NAME);

// Payment methods
export const listPaymentMethods = async (): Promise<PaymentMethod[]> => {
    const response = await fetch('http://localhost:8080/api/cart/payment-methods');
    
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
    const response = await fetch('http://localhost:8080/api/cart', {
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
    const cartLines: CartLine[] = responseData.cart_lines;

    return cartLines
}

// Add item to cart
export const addToCart = async (productId: number, quantity: number): Promise<string> => {
    const payload = {
        id: null,
        component_id: productId,
        quantity: quantity
    };
    
    const response = await fetch("http://localhost:8080/api/cart/add-item", {
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
    const response = await fetch(
        "http://localhost:8080/api/cart/remove-item/" + itemId,
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