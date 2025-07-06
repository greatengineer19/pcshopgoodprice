"use client"

import { useState, useEffect } from "react"
import type { ProductInFrontend, ProductParams } from "@/types/product"

interface DayPricing {
    dayType: string
    pricePerUnit: string
    active: boolean
}

export function useProductForm(initialProduct?: ProductInFrontend) {
    const [formData, setFormData] = useState<ProductParams>({
        id: null,
        name: initialProduct?.name || "",
        product_code: initialProduct?.product_code || "",
        component_category_name: initialProduct?.component_category_name || "",
        description: initialProduct?.description || "",
        image: initialProduct?.image || "/placeholder.svg?height=300&width=300",
        component_category_id: null,
        computer_component_sell_price_settings_attributes: []
    })

    const [dayPricing, setDayPricing] = useState<DayPricing[]>([
        { dayType: "Monday", pricePerUnit: "", active: true},
        { dayType: "Tuesday", pricePerUnit: "", active: true},
        { dayType: "Wednesday", pricePerUnit: "", active: true},
        { dayType: "Thursday", pricePerUnit: "", active: true},
        { dayType: "Friday", pricePerUnit: "", active: true},
        { dayType: "Saturday", pricePerUnit: "", active: true},
        { dayType: "Sunday", pricePerUnit: "", active: true},
    ])

    const [defaultPrice, setDefaultPrice] = useState("")

    useEffect(() => {
        if (initialProduct) {
            setFormData({
                id: null,
                name: initialProduct.name,
                product_code: initialProduct.product_code || "",
                component_category_name: initialProduct.component_category_name,
                description: initialProduct.description,
                image: initialProduct.image,
                component_category_id: null,
                computer_component_sell_price_settings_attributes: []
            })
        }
    }, [initialProduct]);

    const handleChange = (field: keyof ProductInFrontend, value: string | number) => {
        setFormData({
            ...formData,
            [field]: value,
        })
    }

    const resetForm = () => {
        setFormData({
            id: null,
            name: initialProduct?.name || "",
            product_code: initialProduct?.product_code || "",
            component_category_name: initialProduct?.component_category_name || "",
            description: initialProduct?.description || "",
            image: initialProduct?.image || "/placeholder.svg?height=300&width=300",
            component_category_id: null,
            computer_component_sell_price_settings_attributes: []
        })

        setDayPricing([
            { dayType: "Monday", pricePerUnit: "", active: true },
            { dayType: "Tuesday", pricePerUnit: "", active: true },
            { dayType: "Wednesday", pricePerUnit: "", active: true },
            { dayType: "Thursday", pricePerUnit: "", active: true },
            { dayType: "Friday", pricePerUnit: "", active: true },
            { dayType: "Saturday", pricePerUnit: "", active: true },
            { dayType: "Sunday", pricePerUnit: "", active: true },
        ])

        setDefaultPrice("")
    }

    const validateForm = (): boolean => {
        return !!(formData.name && formData.component_category_name)
    }

    return {
        formData,
        handleChange,
        resetForm,
        validateForm,
        setFormData,
        dayPricing,
        setDayPricing,
        defaultPrice,
        setDefaultPrice
    }
}