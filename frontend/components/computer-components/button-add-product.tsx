import { useProducts } from "@/hooks/use-products"
import Image from "next/image"
import { Button } from "@/components/ui/button"

interface ButtonAddProductProps {
    setIsAddDialogOpen: () => void
}

export function ButtonAddProduct({ setIsAddDialogOpen }: ButtonAddProductProps) {
    const handleAddProduct = () => {
        setIsAddDialogOpen()
    }

    return (
        <Button 
            type="button" 
            onClick={handleAddProduct} 
            className="flex items-center gap-2 bg-[#D84040] hover:bg-[#383838] dark:hover:bg-[#E85050] text-white"
        >
            <Image
                src="/plus.svg"
                alt="Add product"
                width={20}
                height={20}
                className="w-5 h-5"
            />
            <span className="hidden sm:inline">Add Product</span>
            <span className="sm:hidden">Add</span>
        </Button>
    )
}