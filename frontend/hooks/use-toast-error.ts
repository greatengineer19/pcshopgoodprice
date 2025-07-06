import { toast } from "sonner"

export function useToastError() {
    const showErrorToast = (message: string) => {
        toast.error(message, {
            style: { backgroundColor: "#D84040", color: "white "},
            position: "top-right",
            closeButton: true,
        })
    }

    return { showErrorToast }
}