import type { CartLine } from "./cart"

export interface SalesQuoteParam {
    id: null,
    customer_id: number,
    customer_name: string,
    shipping_address: string,
    payment_method_id: number,
    payment_method_name: string,
    virtual_account_no: string,
    paylater_account_reference: string,
    credit_card_customer_name: string,
    credit_card_customer_address: string,
    credit_card_bank_name: string,
    cart_lines: CartLine[]
}

export interface SalesQuoteLine {
    id: number
    sales_quote_id: number
    component_id: number
    component_name: string
    quantity: number
    images: string[] | null
    price_per_unit: number
    total_line_amount: number
    created_at: string
    updated_at: string
}

export interface SalesQuote {
    id: number
    customer_id: number
    customer_name: string
    shipping_address: string
    payment_method_id: number
    payment_method_name: string
    virtual_account_no: string | null
    paylater_account_reference: string | null
    credit_card_customer_name: string | null
    credit_card_customer_address: string | null
    credit_card_bank_name: string | null
    sales_quote_no: string
    sum_total_line_amounts: number
    total_payable_amount: number
    created_at: string
    updated_at: string
    sales_quote_lines: SalesQuoteLine[]
}