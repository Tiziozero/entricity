import math
def get_contrasting_color(color):
    # Simple logic to get a contrasting color
    r, g, b, _ = color
    brightness = (r*0.299 + g*0.587 + b*0.114)
    if brightness > 128:
        return 0x000000
    else:
        return 0xffffff

def divide_array_evenly(array, num_slices=24):
    # Calculate base slice size and remainder
    base_size = len(array) // num_slices
    remainder = len(array) % num_slices
    
    # Create a list to hold the slices
    slices = []
    start = 0
    
    for i in range(num_slices):
        # Calculate the end index for the current slice
        end = start + base_size + (1 if i < remainder else 0)
        # Append the slice to the list
        slices.append(array[start:end])
        # Update the start index for the next slice
        start = end
    
    return slices
def float_to_sf(number, significant_figures):
    if number == 0:
        return f"0.{'0' * (significant_figures - 1)}"
    return f"{number:.{significant_figures}g}"
def find_factors(number) -> set:
    factors = set()
    for i in range(1, int(math.sqrt(number)) + 1):
        if number % i == 0:
            factors.add(i)
            factors.add(number // i)
    return factors
def find_prime_factors(n) -> set:
    prime_factors = set()
    # Start with the smallest prime factor
    divisor = 2
    while divisor <= n:
        if n % divisor == 0:
            prime_factors.add(divisor)
            n //= divisor
        else:
            divisor += 1
    return prime_factors

def largest_common_factor_less_than_n(num1, num2, n) -> int | None:
    factors_num1 = find_factors(num1)
    factors_num2 = find_factors(num2)
    

    common_factors = factors_num1.intersection(factors_num2)
    common_factors_less_than_n = [factor for factor in common_factors if factor < n]
    

    if not common_factors_less_than_n:
        return None
    
    return max(common_factors_less_than_n)
