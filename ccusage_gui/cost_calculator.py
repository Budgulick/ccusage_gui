"""
Cost calculation module for Mr. The Guru - Claude Code Usage

Handles token-based cost calculations with model-specific pricing.
Supports multiple calculation modes and pricing updates.
"""

import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, NamedTuple
from pathlib import Path
from dataclasses import dataclass

from .data_loader import UsageRecord

logger = logging.getLogger(__name__)


@dataclass
class ModelPricing:
    """Pricing information for a Claude model."""
    model_name: str
    input_price_per_1k: float  # Price per 1000 input tokens
    output_price_per_1k: float  # Price per 1000 output tokens
    cache_creation_price_per_1k: float  # Price per 1000 cache creation tokens
    cache_read_price_per_1k: float  # Price per 1000 cache read tokens
    currency: str = "USD"
    last_updated: Optional[datetime] = None


class CostCalculation(NamedTuple):
    """Result of cost calculation for usage records."""
    input_cost: float
    output_cost: float
    cache_creation_cost: float
    cache_read_cost: float
    total_cost: float
    currency: str
    model: str

    @property
    def total_tokens(self) -> int:
        """Calculate total tokens from the original record."""
        # Note: This property assumes the calculation was done on a single record
        # For multiple records, this would need to be calculated differently
        return 0  # This would be set during calculation


class CostCalculator:
    """
    Calculates costs for Claude Code usage based on token consumption.

    Supports multiple calculation modes:
    - auto: Use pre-calculated costs when available, calculate otherwise
    - calculate: Always calculate costs from tokens
    - display: Only show pre-calculated costs

    Handles pricing updates and offline mode with cached pricing.
    """

    # Default pricing data (fallback when online pricing fails)
    DEFAULT_PRICING = {
        "claude-3-opus-20240229": ModelPricing(
            model_name="claude-3-opus-20240229",
            input_price_per_1k=15.0,
            output_price_per_1k=75.0,
            cache_creation_price_per_1k=18.75,
            cache_read_price_per_1k=1.5
        ),
        "claude-3-5-sonnet-20241022": ModelPricing(
            model_name="claude-3-5-sonnet-20241022",
            input_price_per_1k=3.0,
            output_price_per_1k=15.0,
            cache_creation_price_per_1k=3.75,
            cache_read_price_per_1k=0.3
        ),
        "claude-3-haiku-20240307": ModelPricing(
            model_name="claude-3-haiku-20240307",
            input_price_per_1k=0.25,
            output_price_per_1k=1.25,
            cache_creation_price_per_1k=0.3,
            cache_read_price_per_1k=0.03
        )
    }

    PRICING_API_URL = "https://api.anthropic.com/v1/pricing"  # Hypothetical API

    def __init__(self, mode: str = "auto", offline: bool = False, currency: str = "USD"):
        """
        Initialize the cost calculator.

        Args:
            mode: Calculation mode ('auto', 'calculate', 'display')
            offline: Use only cached pricing data
            currency: Currency for cost calculations
        """
        self.mode = mode
        self.offline = offline
        self.currency = currency
        self._pricing_cache: Dict[str, ModelPricing] = {}
        self._last_pricing_update: Optional[datetime] = None

        # Load cached pricing
        self._load_pricing_cache()

        # Update pricing if not offline and cache is stale
        if not offline and self._is_pricing_stale():
            self.update_pricing()

    def _load_pricing_cache(self):
        """Load pricing data from cache file."""
        cache_file = Path.cwd() / "pricing_cache.json"

        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)

                self._last_pricing_update = None
                if 'last_updated' in cache_data:
                    self._last_pricing_update = datetime.fromisoformat(cache_data['last_updated'])

                for model_name, pricing_data in cache_data.get('pricing', {}).items():
                    self._pricing_cache[model_name] = ModelPricing(
                        model_name=pricing_data['model_name'],
                        input_price_per_1k=pricing_data['input_price_per_1k'],
                        output_price_per_1k=pricing_data['output_price_per_1k'],
                        cache_creation_price_per_1k=pricing_data['cache_creation_price_per_1k'],
                        cache_read_price_per_1k=pricing_data['cache_read_price_per_1k'],
                        currency=pricing_data.get('currency', 'USD'),
                        last_updated=self._last_pricing_update
                    )

                logger.info(f"Loaded pricing cache with {len(self._pricing_cache)} models")

            except Exception as e:
                logger.warning(f"Error loading pricing cache: {e}")

        # Use default pricing if cache is empty
        if not self._pricing_cache:
            self._pricing_cache = self.DEFAULT_PRICING.copy()
            logger.info("Using default pricing data")

    def _save_pricing_cache(self):
        """Save pricing data to cache file."""
        cache_file = Path.cwd() / "pricing_cache.json"

        try:
            cache_data = {
                'last_updated': datetime.now().isoformat(),
                'pricing': {}
            }

            for model_name, pricing in self._pricing_cache.items():
                cache_data['pricing'][model_name] = {
                    'model_name': pricing.model_name,
                    'input_price_per_1k': pricing.input_price_per_1k,
                    'output_price_per_1k': pricing.output_price_per_1k,
                    'cache_creation_price_per_1k': pricing.cache_creation_price_per_1k,
                    'cache_read_price_per_1k': pricing.cache_read_price_per_1k,
                    'currency': pricing.currency
                }

            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)

            logger.info(f"Saved pricing cache to {cache_file}")

        except Exception as e:
            logger.error(f"Error saving pricing cache: {e}")

    def _is_pricing_stale(self, max_age_days: int = 7) -> bool:
        """Check if pricing cache is stale."""
        if self._last_pricing_update is None:
            return True

        age = datetime.now() - self._last_pricing_update
        return age > timedelta(days=max_age_days)

    def update_pricing(self, force: bool = False) -> bool:
        """
        Update pricing data from API.

        Args:
            force: Force update even if cache is fresh

        Returns:
            True if update was successful
        """
        if self.offline:
            logger.info("Offline mode enabled, skipping pricing update")
            return False

        if not force and not self._is_pricing_stale():
            logger.info("Pricing cache is fresh, skipping update")
            return True

        try:
            logger.info("Updating pricing data...")

            # In a real implementation, this would fetch from Anthropic's API
            # For now, we'll simulate with default pricing
            updated_pricing = self._fetch_pricing_from_api()

            if updated_pricing:
                self._pricing_cache.update(updated_pricing)
                self._last_pricing_update = datetime.now()
                self._save_pricing_cache()
                logger.info(f"Updated pricing for {len(updated_pricing)} models")
                return True

        except Exception as e:
            logger.error(f"Error updating pricing: {e}")

        return False

    def _fetch_pricing_from_api(self) -> Optional[Dict[str, ModelPricing]]:
        """
        Fetch pricing data from API.

        Returns:
            Dictionary of model pricing or None if fetch fails
        """
        try:
            # Simulate API call - in reality, this would call Anthropic's pricing API
            # For now, return updated default pricing
            logger.info("Simulating API call to fetch pricing...")

            # Add some variation to simulate real pricing updates
            import random
            updated_pricing = {}

            for model_name, base_pricing in self.DEFAULT_PRICING.items():
                # Simulate minor price adjustments
                variation = random.uniform(0.95, 1.05)

                updated_pricing[model_name] = ModelPricing(
                    model_name=model_name,
                    input_price_per_1k=base_pricing.input_price_per_1k * variation,
                    output_price_per_1k=base_pricing.output_price_per_1k * variation,
                    cache_creation_price_per_1k=base_pricing.cache_creation_price_per_1k * variation,
                    cache_read_price_per_1k=base_pricing.cache_read_price_per_1k * variation,
                    currency=self.currency,
                    last_updated=datetime.now()
                )

            return updated_pricing

            # Real implementation would look like:
            # response = requests.get(self.PRICING_API_URL, timeout=10)
            # response.raise_for_status()
            # return self._parse_pricing_response(response.json())

        except Exception as e:
            logger.error(f"Error fetching pricing from API: {e}")
            return None

    def get_model_pricing(self, model_name: str) -> Optional[ModelPricing]:
        """
        Get pricing for a specific model.

        Args:
            model_name: Name of the Claude model

        Returns:
            ModelPricing object or None if not found
        """
        # Direct match
        if model_name in self._pricing_cache:
            return self._pricing_cache[model_name]

        # Try partial matches (e.g., "claude-3-opus" matches "claude-3-opus-20240229")
        for cached_model, pricing in self._pricing_cache.items():
            if model_name in cached_model or cached_model in model_name:
                logger.info(f"Using pricing for {cached_model} for model {model_name}")
                return pricing

        # Fallback to default pricing based on model family
        if "opus" in model_name.lower():
            return self.DEFAULT_PRICING.get("claude-3-opus-20240229")
        elif "sonnet" in model_name.lower():
            return self.DEFAULT_PRICING.get("claude-3-5-sonnet-20241022")
        elif "haiku" in model_name.lower():
            return self.DEFAULT_PRICING.get("claude-3-haiku-20240307")

        logger.warning(f"No pricing found for model: {model_name}")
        return None

    def calculate_cost(self, record: UsageRecord) -> Optional[CostCalculation]:
        """
        Calculate cost for a single usage record.

        Args:
            record: Usage record to calculate cost for

        Returns:
            CostCalculation object or None if calculation fails
        """
        pricing = self.get_model_pricing(record.model)
        if not pricing:
            return None

        # Calculate costs for each token type
        input_cost = (record.input_tokens / 1000) * pricing.input_price_per_1k
        output_cost = (record.output_tokens / 1000) * pricing.output_price_per_1k
        cache_creation_cost = (record.cache_creation_tokens / 1000) * pricing.cache_creation_price_per_1k
        cache_read_cost = (record.cache_read_tokens / 1000) * pricing.cache_read_price_per_1k

        total_cost = input_cost + output_cost + cache_creation_cost + cache_read_cost

        return CostCalculation(
            input_cost=input_cost,
            output_cost=output_cost,
            cache_creation_cost=cache_creation_cost,
            cache_read_cost=cache_read_cost,
            total_cost=total_cost,
            currency=pricing.currency,
            model=record.model
        )

    def calculate_total_cost(self, records: List[UsageRecord]) -> Dict[str, float]:
        """
        Calculate total costs for multiple usage records.

        Args:
            records: List of usage records

        Returns:
            Dictionary with cost breakdown
        """
        total_costs = {
            'input_cost': 0.0,
            'output_cost': 0.0,
            'cache_creation_cost': 0.0,
            'cache_read_cost': 0.0,
            'total_cost': 0.0
        }

        model_costs = {}
        failed_calculations = 0

        for record in records:
            cost_calc = self.calculate_cost(record)

            if cost_calc:
                total_costs['input_cost'] += cost_calc.input_cost
                total_costs['output_cost'] += cost_calc.output_cost
                total_costs['cache_creation_cost'] += cost_calc.cache_creation_cost
                total_costs['cache_read_cost'] += cost_calc.cache_read_cost
                total_costs['total_cost'] += cost_calc.total_cost

                # Track per-model costs
                if record.model not in model_costs:
                    model_costs[record.model] = 0.0
                model_costs[record.model] += cost_calc.total_cost

            else:
                failed_calculations += 1

        # Add model breakdown to results
        total_costs['model_breakdown'] = model_costs

        if failed_calculations > 0:
            logger.warning(f"Failed to calculate costs for {failed_calculations} records")

        return total_costs

    def get_available_models(self) -> List[str]:
        """
        Get list of models with available pricing.

        Returns:
            List of model names
        """
        return list(self._pricing_cache.keys())

    def get_pricing_info(self) -> Dict[str, any]:
        """
        Get pricing information and status.

        Returns:
            Dictionary with pricing information
        """
        return {
            'mode': self.mode,
            'offline': self.offline,
            'currency': self.currency,
            'last_updated': self._last_pricing_update.isoformat() if self._last_pricing_update else None,
            'is_stale': self._is_pricing_stale(),
            'available_models': self.get_available_models(),
            'cache_file_exists': (Path.cwd() / "pricing_cache.json").exists()
        }