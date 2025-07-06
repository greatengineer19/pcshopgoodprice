export const getStatusColor = (status: string | number): string => {
    // If status is a number, convert it to string
    const statusStr = typeof status === 'number' 
        ? ['PENDING', 'PROCESSING', 'COMPLETED', 'CANCELLED'][status] 
        : status.toUpperCase();  // Convert to uppercase to match our cases
    
    let color = "bg-gray-500"; // default color
    
    switch (statusStr) {
        case "COMPLETED":
            color = "bg-green-500";
            break;
        case "PROCESSING":
            color = "bg-blue-500";
            break;
        case "PENDING":
            color = "bg-yellow-500";
            break;
        case "CANCELLED":
            color = "bg-red-500";
            break;
    }
    
    return color;
}