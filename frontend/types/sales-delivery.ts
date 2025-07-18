export interface SalesDeliveryLine {
    id: number
    sales_delivery_id: number
    component_id: number
    component_name: string
    quantity: number
    created_at: string
    updated_at: string
}

export interface SalesDelivery {
    id: number
    status: string
    customer_id: number
    customer_name: string
    shipping_address: string
    sales_invoice_id: number
    sales_delivery_no: string
    created_at: string
    updated_at: string
    sales_delivery_lines: SalesDeliveryLine[]
}