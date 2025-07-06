import ShopContent from "@/components/shop/ShopContent"
import { fetchSellableProducts } from "@/lib/api"

export default function ShopPage() {
    const products = await fetchSellableProducts();

    return <ShopContent products={products}/>
}
