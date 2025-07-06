export interface InboundDelivery {
  id: string
  inbound_delivery_no: string
  purchase_invoice_no: string
  purchase_invoice_id: string
  inbound_delivery_date: string
  inbound_delivery_reference: string
  received_by: string
  status: "Received" | string
  notes: string
  created_at: string
  updated_at: string
  deleted: boolean
  inbound_delivery_attachments: InboundDeliveryAttachment[]
  inbound_delivery_lines: InboundDeliveryLine[]
}
  
export interface InboundDeliveryLine {
  id: string
  inbound_delivery_id: string
  purchase_invoice_line_id: string
  component_id: number
  component_name: string
  component_category_id: string
  component_category_name: string
  expected_quantity: number
  received_quantity: number
  damaged_quantity: number
  price_per_unit: number
  total_line_amount: number
  notes: string
  deleted: boolean
}

export interface InboundDeliveryAttachment {
  id: number
  inbound_delivery_id: number
  file_link: string
  file_s3_key: string
  uploaded_by: string
  created_at: string
  updated_at: string
}

export interface InboundDeliveryFormData {
  purchase_invoice_id: number | null
  purchase_invoice_no: string
  inbound_delivery_date: string
  inbound_delivery_reference: string
  received_by: string
  notes: string
  inbound_delivery_lines_attributes: InboundDeliveryLineFormData[]
  inbound_delivery_attachments_attributes: File[]
}

export interface InboundDeliveryLineFormData {
  purchase_invoice_line_id: number
  component_id: number
  expected_quantity: number
  received_quantity: number
  damaged_quantity: number
  notes: string
  price_per_unit: number
}
  