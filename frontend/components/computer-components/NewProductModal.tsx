"use client"

import type React from "react"

import { Upload } from "lucide-react"
import Image from "next/image"
import { useRef } from "react"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useProductForm } from "@/hooks/use-product-form"
import { UploadedImageResponse } from "@/types/image"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Switch } from "@/components/ui/switch"

import type { ProductParams, DailyProductPrice } from "@/types/product"
import { useToastSuccess } from "@/hooks/use-toast-success"
import { useToastError } from "@/hooks/use-toast-error"
import { handleApiError } from "@/utils/api/error-handlers"
import { categories } from "@/utils/computer-component/categories"
import { Dispatch, SetStateAction } from "react";

interface NewProductModalProps {
    setIsLoading: React.Dispatch<React.SetStateAction<boolean>>,
    isAddDialogOpen: boolean,
    setIsAddDialogOpen: React.Dispatch<React.SetStateAction<boolean>>,
    isLoading: boolean,
    uploadedImage: UploadedImageResponse | null,
    handleFileSelect: (event: React.ChangeEvent<HTMLInputElement>) => void,
    setPreviewUrl: Dispatch<SetStateAction<string>>,
    previewUrl: string
}

interface DayPricing {
    day: string
    price: string
    active: boolean
}

export function NewProductModal({
        setIsLoading,
        isAddDialogOpen,
        setIsAddDialogOpen,
        isLoading,
        uploadedImage,
        handleFileSelect,
        setPreviewUrl,
        previewUrl
    }: NewProductModalProps) {
    const { formData, handleChange, resetForm, setDayPricing, dayPricing, defaultPrice, setDefaultPrice } = useProductForm()
    const newProduct = formData
    const fileInputRef = useRef<HTMLInputElement>(null);
    const handleUploadClick = () => {
		fileInputRef.current?.click();
	};
    const { showErrorToast } = useToastError()
    const { showSuccessToast } = useToastSuccess()

    const handlePriceChange = (index: number, price: string) => {
        const updated = [...dayPricing]
        updated[index].pricePerUnit = price
        setDayPricing(updated)
    }

    const handleActiveToggle = (index: number, active: boolean) => {
        const updated = [...dayPricing]
        updated[index].active = active
        setDayPricing(updated)
    }

    const handleSubmitNewProduct = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setIsLoading(true);
      
        try {
          if (!newProduct.name || !newProduct.component_category_name || !newProduct.price) {
            showErrorToast("Please fill in all required fields");
            return;
          }
      
          const imageUrl = uploadedImage?.s3_key;

          // 1. Create the default price setting
          const defaultPriceSetting = {
                id: null,
                day_type: 'default',
                price_per_unit: Number(defaultPrice), // Ensure it's a number
                active: true // Default price is always active
            };
            
          // 2. Create the daily price settings
          const dailyPriceSettings = dayPricing // Only include active days with a positive price
              .map((day) => ({
                  id: null,
                  day_type: day.dayType.toLowerCase(), // Convert 'Monday' to 'monday'
                  price_per_unit: Number(day.pricePerUnit), // Ensure it's a number
                  active: true // These are active because they passed the filter
              }));

          // 3. Combine all price settings
          const computer_component_sell_price_settings_attributes = [
              defaultPriceSetting,
              ...dailyPriceSettings
          ];
      
          const payload: ProductParams = {
            ...newProduct,
            id: null,
            category_id: null,
            status: 0,
            created_at: null,
            updated_at: null,
            images: imageUrl ? [imageUrl] : [],
            price: Number(newProduct.price) ?? 0,
            stock: Number(newProduct.stock) ?? 0,
            computer_component_sell_price_settings_attributes: computer_component_sell_price_settings_attributes
          };
      
          const response = await fetch("http://localhost:8080/api/computer-components", {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
          });
      
          if (!response.ok) {
            await handleApiError(response, showErrorToast);
            return;
          }
      
          const data = await response.json();
          showSuccessToast(data.message || "Product created successfully");
      
          // Reset form state
          resetForm()
          setPreviewUrl("/placeholder.svg?height=300&width=300");
          setIsAddDialogOpen(false);
          window.location.reload();
      
        } catch (error) {
          showErrorToast("Failed to create product. Please try again.");
        } finally {
          setIsLoading(false);
        }
    };
      
    const handleClose = () => {
        resetForm()
        setIsAddDialogOpen(false)
    }

    return (
        <Dialog open={isAddDialogOpen} onOpenChange={handleClose}>
            <DialogContent className="sm:max-w-[600px]">
                <DialogHeader>
                    <DialogTitle className="text-x1 font-bold">
                        Add New Product
                    </DialogTitle>
                </DialogHeader>
                <form onSubmit={handleSubmitNewProduct} className="grid gap-4 py-4">
                    <Tabs defaultValue="info" className="w-full">
                        <TabsList className="grid w-full grid-cols-2">
                            <TabsTrigger value="info">Product Info</TabsTrigger>
                            <TabsTrigger value="pricing">Pricing</TabsTrigger>
                        </TabsList>

                        <TabsContent value="info" className="space-y-4 mt-4">
                            <div className="grid gap-2">
                                <Label htmlFor="new-name" className="required">
                                    Name
                                </Label>
                                <Input
                                    id="new-name"
                                    value={newProduct.name}
                                    disabled={isLoading}
                                    onChange={(e) => handleChange("name", e.target.value)}
                                    required
                                />
                            </div>

                            <div className="grid gap-2">
                                <Label htmlFor="new-category" className="required">
                                    Category
                                </Label>
                                <Select
                                    value={newProduct.component_category_name}
                                    onValueChange={(value) => handleChange("component_category_name", value)}
                                    required
                                    disabled={isLoading}
                                >
                                    <SelectTrigger>
                                        <SelectValue placeholder="Select a category"/>
                                    </SelectTrigger>
                                    <SelectContent>
                                        {categories.map((category) => (
                                            <SelectItem key={category} value={category}>
                                                {category}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>

                            <div className="grid gap-2">
                                <Label htmlFor="new-description">
                                    Description
                                </Label>
                                <Textarea
                                    id="new-description"
                                    rows={3}
                                    value={newProduct.description}
                                    disabled={isLoading}
                                    onChange={(e) => handleChange("description", e.target.value)}
                                />
                            </div>

                            <div className="grid gap-2">
                                <Label>Product Image</Label>
                                <div className="flex items-center gap-4">
                                    <div className="relative h-24 w-24 border rounded overflow-hidden">
                                        <Image 
                                            src={previewUrl}
                                            alt="Product preview"
                                            fill
                                            className="object-cover"
                                        />
                                    </div>
                                    <input
                                        type="file"
                                        ref={fileInputRef}
                                        onChange={handleFileSelect}
                                        accept="image/*"
                                        className="hidden"
                                    />
                                    <Button 
                                        type="button" 
                                        variant="outline" 
                                        className="h-10"
                                        onClick={handleUploadClick}
                                        disabled={isLoading}
                                    >
                                        <Upload className="h-4 w-4 mr-2"/>
                                        Upload Image
                                    </Button>
                                </div>
                                <p className="text-sm text-muted-foreground">
                                    Recommended: 1000x1000px, max 5MB
                                </p>
                            </div>

                            <div className="flex justify-end gap-2 mt-4">
                                <Button type="button" variant="outline" disabled={isLoading}
                                    onClick={() => handleClose}>
                                    Cancel
                                </Button>
                                <Button type="submit" disabled={isLoading}>{isLoading ? "Adding..." : "Add Product"}</Button>
                            </div>
                        </TabsContent>

                        <TabsContent value="pricing" className="mt-4">
                            <div className="space-y-4">
                                {/* Default Price */}
                                <div className="flex items-center justify-between p-3 border rounded-lg">
                                    <div className="flex-1">
                                        <Label htmlFor="default-price" className="font-medium">
                                            Default Price
                                        </Label>
                                        <Input 
                                            id="default-price"
                                            type="number"
                                            placeholder="0.00"
                                            value={defaultPrice}
                                            onChange={(e) => setDefaultPrice(e.target.value)}
                                            className="mt-1"
                                            step="0.01"
                                            min="0"
                                        />
                                    </div>

                                    {/* Day Pricing */}
                                    <div className="space-y-2">
                                        <Label className="text-sm font-medium">Daily Pricing (Optional)</Label>
                                        <div className="space-y-2 max-h-64 overflow-y-auto">
                                            {
                                                dayPricing.map((day, index) => (
                                                    <div key={day.dayType} className="flex items-center justify-between p-3 border rounded-lg">
                                                        <div className="flex-1">
                                                            <Label className="font-medium">{day.dayType}</Label>
                                                            <Input 
                                                                type="number"
                                                                placeholder="0.00"
                                                                value={day.pricePerUnit}
                                                                onChange={(e) => handlePriceChange(index, e.target.value)}
                                                                className="mt-1"
                                                                step="1"
                                                                min="0"
                                                            />
                                                            <div className="flex items-center space-x-2 ml-4">
                                                                <Label className="text-sm">Active</Label>
                                                                <Switch 
                                                                    checked={day.active}
                                                                    onCheckedChange={(checked) => handleActiveToggle(index, checked)}
                                                                />
                                                            </div>
                                                        </div>
                                                    </div>
                                                ))
                                            }
                                        </div>
                                        <p className="text-sm text-muted-foreground mt-2">
                                            Activate daily pricing for specific days if different from the default.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </TabsContent>
                    </Tabs>
                </form>
            </DialogContent>
        </Dialog>
    )
}