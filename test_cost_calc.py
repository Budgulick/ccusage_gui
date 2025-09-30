"""Test cost calculation manually"""
from ccusage_gui.data_loader import DataLoader
from ccusage_gui.config import ConfigManager

config = ConfigManager()
loader = DataLoader(config.get_claude_data_paths())
records = loader.load_usage_data()

# Calculate costs manually
input_tokens = sum(r.input_tokens for r in records)
output_tokens = sum(r.output_tokens for r in records)
cache_create = sum(r.cache_creation_tokens for r in records)
cache_read = sum(r.cache_read_tokens for r in records)

print(f'Input tokens: {input_tokens:,}')
print(f'Output tokens: {output_tokens:,}')
print(f'Cache creation: {cache_create:,}')
print(f'Cache read: {cache_read:,}')

# Sonnet 4 pricing ($/MTok - per MILLION tokens)
# Input: $3, Output: $15, Cache Write: $3.75, Cache Read: $0.30
input_cost = (input_tokens / 1_000_000) * 3.0
output_cost = (output_tokens / 1_000_000) * 15.0
cache_create_cost = (cache_create / 1_000_000) * 3.75
cache_read_cost = (cache_read / 1_000_000) * 0.30

print(f'\nEstimated costs (Sonnet 4 pricing):')
print(f'Input: ${input_cost:.2f}')
print(f'Output: ${output_cost:.2f}')
print(f'Cache creation: ${cache_create_cost:.2f}')
print(f'Cache read: ${cache_read_cost:.2f}')
print(f'Total: ${input_cost + output_cost + cache_create_cost + cache_read_cost:.2f}')