import type { SalesQuote, SalesQuoteParam } from "@/types/sales-quote"
import type { CartLine, PaymentMethod } from "@/types/cart"
import { handleApiError } from "@/utils/api/error-handlers"
import { useToastError } from "@/hooks/use-toast-error"
import { useToastSuccess } from "@/hooks/use-toast-success"
import { toast } from "sonner"
import { User } from "@/types/user"

const { showErrorToast } = useToastError()
const { showSuccessToast } = useToastSuccess()
const SECRET_KEY_NAME = 'secret_key';

// Create order
export const createSalesQuote = async (
    cartLines: CartLine[],
    shippingAddress: string,
    paymentInfo: any,
    user: User
): Promise<string> => {
    let token: string | null = null;
    // Todo: need to improve when secret key expired
    if (typeof window !== "undefined") {
        token = localStorage.getItem(SECRET_KEY_NAME);
    }

    const salesQuoteParam: SalesQuoteParam = {
        id: null,
        customer_id: user.id,
        customer_name: user.fullname,
        shipping_address: shippingAddress,
        payment_method_id: paymentInfo.paymentMethodId,
        payment_method_name: paymentInfo.paymentMethodName,
        virtual_account_no: paymentInfo.virtualAccountNo,
        paylater_account_reference: paymentInfo.paylaterAccountReference,
        credit_card_customer_name: paymentInfo.creditCardCustomerName,
        credit_card_customer_address: paymentInfo.creditCardCustomerAddress,
        credit_card_bank_name: paymentInfo.creditCardBankName,
        cart_lines: cartLines
    }

    const response = await fetch('http://localhost:8000/api/sales-quotes', {
        method: 'POST',
        body: JSON.stringify(salesQuoteParam),
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        }
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || "Failed to create sales quote");
    }

    return 'ok'
}

export const destroySalesQuote = async (id: number): Promise<any> => {  
    try {
        let token: string | null = null;
        if (typeof window !== "undefined") {
            token = localStorage.getItem(SECRET_KEY_NAME);
        }

        const response = await fetch(
            "http://localhost:8000/api/sales-quotes/" + id,
            {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    "Authorization": `Bearer ${token}`
                },
            });
            

        if (!response.ok) {
            await handleApiError(response, showErrorToast);
        }

        showSuccessToast("Sales quote deleted successfully");
        return 'ok'
    } catch (error) {
        showErrorToast("Failed to connect to the server. Please try again.");
    }
}

// Fetch Orders
export const fetchSalesQuotes = async (): Promise<SalesQuote[]> => {
    let token: string | null = null;
    if (typeof window !== "undefined") {
        token = localStorage.getItem(SECRET_KEY_NAME);
    }

    const response = await fetch('http://localhost:8000/api/sales-quotes', {
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        }
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || "Failed to fetch sales quotes");
    }

    const responseData = await response.json();
    const salesQuotes: SalesQuote[] = responseData.sales_quotes;

    return salesQuotes
}
