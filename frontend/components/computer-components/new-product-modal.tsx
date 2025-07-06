"use client"

import type React from "react"

import { Upload } from "lucide-react"
import Image from "next/image"
import { useRef } from "react"

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useProductForm } from "@/hooks/use-product-form"
import { UploadedImageResponse } from "@/types/image"

import type { ProductInFrontend, ProductFromBackend } from "@/types/product"
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
    const { formData, handleChange, resetForm } = useProductForm()
    const newProduct = formData
    const fileInputRef = useRef<HTMLInputElement>(null);
    const handleUploadClick = () => {
		fileInputRef.current?.click();
	};
    const { showErrorToast } = useToastError()
    const { showSuccessToast } = useToastSuccess()

    const handleSubmitNewProduct = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setIsLoading(true);
      
        try {
          if (!newProduct.name || !newProduct.component_category_name || !newProduct.price) {
            showErrorToast("Please fill in all required fields");
            return;
          }
      
          const imageUrl = uploadedImage?.s3_key;
      
          const payload: ProductFromBackend = {
            ...newProduct,
            id: null,
            product_code: newProduct.name,
            category_id: null,
            status: 0,
            created_at: null,
            updated_at: null,
            images: imageUrl ? [imageUrl] : [],
            price: Number(newProduct.price) ?? 0,
            stock: Number(newProduct.stock) ?? 0,
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
                        <Label htmlFor="new-price" className="required">
                            Price ($)
                        </Label>
                        <Input 
                            id="new-price"
                            type="number"
                            step="0.01"
                            min="0.01"
                            disabled={isLoading}
                            value={newProduct.price}
                            onChange={(e) => handleChange("price", parseInt(e.target.value, 10))}
                            required
                        />
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

                    <div className="grip gap-2">
                        <Label htmlFor="new-stock">
                                Stock
                        </Label>
                        <Input
                            id="new-stock"
                            type="number"
                            min="0"
                            value={newProduct.stock}
                            disabled={isLoading}
                            onChange={(e) => handleChange("stock", parseFloat(e.target.value) || 0)}
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
                </form>
            </DialogContent>
        </Dialog>
    )
}