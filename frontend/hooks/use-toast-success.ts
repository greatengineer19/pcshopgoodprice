import { toast } from "sonner"

export function useToastSuccess() {
    const showSuccessToast = (message: string) => {
		toast.success(message, {
			style: { backgroundColor: "#10B981", color: "white" },
			position: "top-right",
			closeButton: true,
		})
	}

    return { showSuccessToast }
}