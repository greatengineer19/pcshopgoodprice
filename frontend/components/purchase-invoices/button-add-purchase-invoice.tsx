import Image from "next/image"
import { Button } from "@/components/ui/button"

interface ButtonAddProps {
    handleOnClick: () => void
}

export function ButtonAddPurchaseInvoice({ handleOnClick }: ButtonAddProps) {
    return (
        <Button 
            type="button" 
            onClick={handleOnClick} 
            className="flex items-center gap-2 bg-[#D84040] hover:bg-[#383838] dark:hover:bg-[#E85050] text-white"
        >
            <Image
                src="/plus.svg"
                alt="Add product"
                width={20}
                height={20}
                className="w-5 h-5"
            />
            <span className="hidden sm:inline">Add Invoice</span>
            <span className="sm:hidden">Add</span>
        </Button>
    )
}