import type { SalesInvoice, SalesInvoiceParam } from "@/types/sales-invoice"
import { handleApiError } from "@/utils/api/error-handlers"
import { useToastError } from "@/hooks/use-toast-error"
import { useToastSuccess } from "@/hooks/use-toast-success"

const { showErrorToast } = useToastError()
const { showSuccessToast } = useToastSuccess()
const SECRET_KEY_NAME = 'secret_key';

// Create order
export const createSalesInvoice = async (
    sales_quote_id: number,
    sales_quote_no: string
): Promise<string> => {
    let token: string | null = null;
    // Todo: need to improve when secret key expired
    if (typeof window !== "undefined") {
        token = localStorage.getItem(SECRET_KEY_NAME);
    }

    const salesInvoiceParam: SalesInvoiceParam = {
        id: null,
        sales_quote_id: sales_quote_id,
        sales_quote_no: sales_quote_no
    }

    const response = await fetch('http://localhost:80/api/sales-invoices', {
        method: 'POST',
        body: JSON.stringify(salesInvoiceParam),
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        }
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || "Failed to create sales invoices");
    }

    return 'ok'
}

export const voidSalesInvoice = async (id: number): Promise<any> => {  
    try {
        let token: string | null = null;
        if (typeof window !== "undefined") {
            token = localStorage.getItem(SECRET_KEY_NAME);
        }

        const response = await fetch(
            "http://localhost:80/api/sales-invoices/" + id  + "/void",
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

        showSuccessToast("Sales invoice voided successfully");
        return 'ok'
    } catch (error) {
        showErrorToast("Failed to connect to the server. Please try again.");
    }
}

// Fetch Orders
export const fetchSalesInvoices = async (): Promise<SalesInvoice[]> => {
    let token: string | null = null;
    if (typeof window !== "undefined") {
        token = localStorage.getItem(SECRET_KEY_NAME);
    }

    const response = await fetch('http://localhost:80/api/sales-invoices', {
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        }
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || "Failed to fetch sales invoices");
    }

    const responseData = await response.json();
    const salesInvoices: SalesInvoice[] = responseData.sales_invoices;

    return salesInvoices
}
