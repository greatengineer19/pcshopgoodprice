import type { SalesDelivery } from "@/types/sales-delivery"
import { handleApiError } from "@/utils/api/error-handlers"
import { useToastError } from "@/hooks/use-toast-error"
import { useToastSuccess } from "@/hooks/use-toast-success"

const { showErrorToast } = useToastError()
const { showSuccessToast } = useToastSuccess()
const SECRET_KEY_NAME = 'secret_key';

export const voidSalesDelivery = async (id: number): Promise<any> => {  
    try {
        let token: string | null = null;
        if (typeof window !== "undefined") {
            token = localStorage.getItem(SECRET_KEY_NAME);
        }

        const response = await fetch(
            "http://localhost:8000/api/sales-deliveries/" + id  + "/void",
            {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    "Authorization": `Bearer ${token}`
                },
            });
            

        if (!response.ok) {
            await handleApiError(response, showErrorToast);
        }

        showSuccessToast("Sales delivery voided successfully");
        return 'ok'
    } catch (error) {
        showErrorToast("Failed to connect to the server. Please try again.");
    }
}

export const fullyDelivered = async (id: number): Promise<any> => {  
    try {
        let token: string | null = null;
        if (typeof window !== "undefined") {
            token = localStorage.getItem(SECRET_KEY_NAME);
        }

        const response = await fetch(
            "http://localhost:8000/api/sales-deliveries/" + id  + "/fully_delivered",
            {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    "Authorization": `Bearer ${token}`
                },
            });
            

        if (!response.ok) {
            await handleApiError(response, showErrorToast);
        }

        showSuccessToast("Sales delivery received successfully");
        return 'ok'
    } catch (error) {
        showErrorToast("Failed to connect to the server. Please try again.");
    }
}

// Fetch Orders
export const fetchSalesDeliveries = async (): Promise<SalesDelivery[]> => {
    let token: string | null = null;
    if (typeof window !== "undefined") {
        token = localStorage.getItem(SECRET_KEY_NAME);
    }

    const response = await fetch('http://localhost:8000/api/sales-deliveries', {
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        }
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || "Failed to fetch sales deliveries");
    }

    const responseData = await response.json();
    const salesDeliveries: SalesDelivery[] = responseData.sales_deliveries;

    return salesDeliveries
}
