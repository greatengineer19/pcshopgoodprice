import CartContent from "@/components/cart/CartContent"
import { userId } from "@/lib/api"

export default function CartPage() {
    return <CartContent userId = {userId} />
}