export interface CartLine {
    id: number
    status: number
    customer_id: number
    componend_id: number
    customer_name: string
    component_name: string
    quantity: number
    sell_price: number
    created_at: string
    updated_at: string
}

export interface PaymentMethod {
    id: number
    name: string
}