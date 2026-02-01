import time
import httpx

def benchmark_client_creation(count=1000):
    start_time = time.perf_counter()
    for _ in range(count):
        with httpx.Client() as client:
            pass
    end_time = time.perf_counter()
    total_time = end_time - start_time
    print(f"Time to create and close {count} httpx.Clients: {total_time:.4f} seconds")
    print(f"Average time per client: {(total_time / count) * 1000:.4f} ms")

if __name__ == "__main__":
    benchmark_client_creation()
