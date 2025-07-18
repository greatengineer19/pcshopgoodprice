export interface SalesInvoiceParam {
    id: null,
    sales_quote_id: number,
    sales_quote_no: string
}

export interface SalesInvoiceLine {
    id: number
    sales_invoice_id: number
    component_id: number
    component_name: string
    quantity: number
    price_per_unit: number
    images: string[] | null
    total_line_amount: number
    created_at: string
    updated_at: string
}

export interface SalesInvoice {
    id: number
    status: string
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
    sales_invoice_no: string
    sum_total_line_amounts: number
    total_payable_amount: number
    created_at: string
    updated_at: string
    sales_invoice_lines: SalesInvoiceLine[]
}