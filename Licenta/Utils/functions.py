
def split_into_chunks(bitstring, chunk_size):
    chunk_size = max(1, chunk_size)
    return (bitstring[i:i + chunk_size] for i in range(0, len(bitstring), chunk_size))
