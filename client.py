"""Distributed ID Snowflake Generator.
100% Python Standard Library.
"""
import time
from typing import Dict, Any, List

class SnowflakeIDGenerator:
    """64-bit Twitter Snowflake-compatible distributed unique ID generator."""
    EPOCH = 1704067200000 # 2024-01-01 00:00:00 UTC in ms
    WORKER_ID_BITS = 10
    SEQUENCE_BITS = 12

    MAX_WORKER_ID = (1 << WORKER_ID_BITS) - 1
    MAX_SEQUENCE = (1 << SEQUENCE_BITS) - 1

    WORKER_SHIFT = SEQUENCE_BITS
    TIMESTAMP_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS

    def __init__(self, worker_id: int = 1):
        if worker_id < 0 or worker_id > self.MAX_WORKER_ID:
            raise ValueError(f"Worker ID must be between 0 and {self.MAX_WORKER_ID}")
        self.worker_id = worker_id
        self.sequence = 0
        self.last_timestamp = -1
        self.total_generated = 0

    def _current_timestamp_ms(self) -> int:
        return int(time.time() * 1000)

    def generate_id(self) -> int:
        ts = self._current_timestamp_ms()

        if ts < self.last_timestamp:
            drift = self.last_timestamp - ts
            if drift <= 100:
                time.sleep(drift / 1000.0)
                ts = self._current_timestamp_ms()
            else:
                raise RuntimeError(f"Clock moved backwards by {drift}ms")

        if ts == self.last_timestamp:
            self.sequence = (self.sequence + 1) & self.MAX_SEQUENCE
            if self.sequence == 0:
                while ts <= self.last_timestamp:
                    ts = self._current_timestamp_ms()
        else:
            self.sequence = 0

        self.last_timestamp = ts
        self.total_generated += 1

        snowflake_id = ((ts - self.EPOCH) << self.TIMESTAMP_SHIFT) | (self.worker_id << self.WORKER_SHIFT) | self.sequence
        return snowflake_id

    def generate_batch(self, count: int = 10) -> List[int]:
        return [self.generate_id() for _ in range(count)]

    @classmethod
    def parse_id(cls, snowflake_id: int) -> Dict[str, Any]:
        sequence = snowflake_id & cls.MAX_SEQUENCE
        worker_id = (snowflake_id >> cls.WORKER_SHIFT) & cls.MAX_WORKER_ID
        timestamp_ms = (snowflake_id >> cls.TIMESTAMP_SHIFT) + cls.EPOCH
        return {
            "snowflake_id": snowflake_id,
            "timestamp_ms": timestamp_ms,
            "worker_id": worker_id,
            "sequence": sequence
        }
