export interface PurchaseInvoiceLine {
    id?: number | null
    component_id: number
    component_name: string
    component_category_id: number
    component_category_name: string
    quantity: number
    price_per_unit: number
    [key: string]: any
}

export interface PurchaseInvoiceBase {
    id?: number | null
    supplier_name: string
    expected_delivery_date: string | null
    invoice_date: string
    notes: string | null
}

export interface PurchaseInvoice extends PurchaseInvoiceBase {
    purchase_invoice_no: string
    status: string
    deleted: boolean
    sum_total_line_amounts: number
    purchase_invoice_lines: PurchaseInvoiceLine[]
    [key: string]: any
}

export interface PurchaseInvoiceToBackend extends PurchaseInvoiceBase {
    purchase_invoice_lines_attributes: PurchaseInvoiceLine[]
}

export interface OnEditPurchaseInvoiceLine {
    id?: number | null
    component_id: number
    component_name: string
    quantity: number
    price: number
    stock: number
    component_category_id: number
    component_category_name: string
}

export interface MappedProduct {
    id: number
    name: string
    quantity: number
    price: number
    stock: number
    component_category_id: number
    component_category_name: string
}

export interface PurchaseForm {
    supplierName: string
    expectedDeliveryDate: string | null
    notes: string | null
    selectedInvoiceLines: OnEditPurchaseInvoiceLine[]
}

export interface DeliverablePurchaseInvoice {
    id: number
    purchase_invoice_no: string
    invoice_date: string
    supplier_name: string
    deliverable_invoice_lines: DeliverablePurchaseInvoiceLine[]
}

export interface DeliverablePurchaseInvoiceLine {
    id: number
    component_id: number
    component_name: string
    component_category_id: number
    component_category_name: string
    deliverable_quantity: number
    price_per_unit: number
}