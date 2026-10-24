"""Example usage for GenPark Distributed ID Snowflake Generator."""
from client import SnowflakeIDGenerator

def main():
    gen = SnowflakeIDGenerator(worker_id=101)
    print("Generating single distributed event ID...")
    event_id = gen.generate_id()
    print(f"Generated Snowflake ID: {event_id}")

    print("
Parsing Snowflake ID components:")
    parsed = SnowflakeIDGenerator.parse_id(event_id)
    print(f" - Timestamp (ms): {parsed['timestamp_ms']}")
    print(f" - Worker ID:     {parsed['worker_id']}")
    print(f" - Sequence:      {parsed['sequence']}")

    print("
Generating batch of 5 IDs:")
    batch = gen.generate_batch(5)
    for i, id_val in enumerate(batch):
        print(f" [{i+1}] {id_val}")

if __name__ == "__main__":
    main()
