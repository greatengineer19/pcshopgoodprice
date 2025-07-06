"use client"

import { useState, useEffect } from "react"
import type { ProductInFrontend } from "@/types/product"

export function useProductForm(initialProduct?: ProductInFrontend) {
    const [formData, setFormData] = useState<ProductInFrontend>({
        id: null,
        name: initialProduct?.name || "",
        component_category_name: initialProduct?.component_category_name || "",
        price: initialProduct?.price || "",
        description: initialProduct?.description || "",
        stock: initialProduct?.stock || "",
        image: initialProduct?.image || "/placeholder.svg?height=300&width=300",
    })

    useEffect(() => {
        if (initialProduct) {
            setFormData({
                id: null,
                name: initialProduct.name,
                component_category_name: initialProduct.component_category_name,
                price: initialProduct.price,
                description: initialProduct.description,
                stock: initialProduct.stock,
                image: initialProduct.image,
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
            component_category_name: initialProduct?.component_category_name || "",
            price: initialProduct?.price || "",
            description: initialProduct?.description || "",
            stock: initialProduct?.stock || "",
            image: initialProduct?.image || "/placeholder.svg?height=300&width=300",
        })
    }

    const validateForm = (): boolean => {
        return !!(formData.name && formData.component_category_name && formData.price)
    }

    return {
        formData,
        handleChange,
        resetForm,
        validateForm,
        setFormData
    }
}