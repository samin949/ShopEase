from abc import ABC, abstractmethod
from typing import List

class PriceCalculator(ABC):
    """Abstract base class for price calculation"""
    @abstractmethod
    def calculate_price(self, original_price: float, quantity: int = 1) -> float:
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        pass


class BasePriceCalculator(PriceCalculator):
    """Concrete component - calculates base price without any discounts"""
    def calculate_price(self, original_price: float, quantity: int = 1) -> float:
        return original_price * quantity
    
    def get_description(self) -> str:
        return "Base Price"


class DiscountDecorator(PriceCalculator):
    """Base decorator class"""
    def __init__(self, calculator: PriceCalculator):
        self._calculator = calculator
    
    def calculate_price(self, original_price: float, quantity: int = 1) -> float:
        return self._calculator.calculate_price(original_price, quantity)
    
    def get_description(self) -> str:
        return self._calculator.get_description()


class PercentageDiscountDecorator(DiscountDecorator):
    """Percentage discount decorator (e.g., 20% off)"""
    def __init__(self, calculator: PriceCalculator, percentage: float):
        super().__init__(calculator)
        self.percentage = percentage
    
    def calculate_price(self, original_price: float, quantity: int = 1) -> float:
        base_price = self._calculator.calculate_price(original_price, quantity)
        discount_amount = base_price * (self.percentage / 100)
        return max(0, base_price - discount_amount)
    
    def get_description(self) -> str:
        return f"{self._calculator.get_description()} + {self.percentage}% off"


class FixedAmountDiscountDecorator(DiscountDecorator):
    """Fixed amount discount decorator (e.g., $10 off)"""
    def __init__(self, calculator: PriceCalculator, amount: float):
        super().__init__(calculator)
        self.amount = amount
    
    def calculate_price(self, original_price: float, quantity: int = 1) -> float:
        base_price = self._calculator.calculate_price(original_price, quantity)
        return max(0, base_price - self.amount)
    
    def get_description(self) -> str:
        return f"{self._calculator.get_description()} + ${self.amount:.2f} off"


class CouponDiscountDecorator(DiscountDecorator):
    """Coupon-based discount decorator"""
    def __init__(self, calculator: PriceCalculator, coupon_code: str, discount_percentage: float):
        super().__init__(calculator)
        self.coupon_code = coupon_code
        self.discount_percentage = discount_percentage
    
    def calculate_price(self, original_price: float, quantity: int = 1) -> float:
        base_price = self._calculator.calculate_price(original_price, quantity)
        if self.validate_coupon():
            discount_amount = base_price * (self.discount_percentage / 100)
            return max(0, base_price - discount_amount)
        return base_price
    
    def validate_coupon(self) -> bool:
        # In a real app, you'd check against a database
        valid_coupons = {
            "SAVE10": True,
            "WELCOME20": True,
            "SUMMER25": True
        }
        return self.coupon_code in valid_coupons
    
    def get_description(self) -> str:
        if self.validate_coupon():
            return f"{self._calculator.get_description()} + Coupon {self.coupon_code} ({self.discount_percentage}% off)"
        return self._calculator.get_description()


class BulkDiscountDecorator(DiscountDecorator):
    """Bulk purchase discount decorator"""
    def __init__(self, calculator: PriceCalculator, min_quantity: int, discount_percentage: float):
        super().__init__(calculator)
        self.min_quantity = min_quantity
        self.discount_percentage = discount_percentage
    
    def calculate_price(self, original_price: float, quantity: int = 1) -> float:
        base_price = self._calculator.calculate_price(original_price, quantity)
        
        if quantity >= self.min_quantity:
            discount_amount = base_price * (self.discount_percentage / 100)
            return max(0, base_price - discount_amount)
        return base_price
    
    def get_description(self) -> str:
        return f"{self._calculator.get_description()} + Bulk ({self.min_quantity}+ items, {self.discount_percentage}% off)"


class DiscountFactory:
    """Factory to create discount combinations"""
    @staticmethod
    def create_discount_calculator(discount_types: List[dict], original_calculator: PriceCalculator = None):
        calculator = original_calculator or BasePriceCalculator()
        
        for discount in discount_types:
            discount_type = discount.get('type')
            
            if discount_type == 'percentage':
                calculator = PercentageDiscountDecorator(
                    calculator, 
                    discount.get('percentage', 0)
                )
            elif discount_type == 'fixed':
                calculator = FixedAmountDiscountDecorator(
                    calculator,
                    discount.get('amount', 0)
                )
            elif discount_type == 'coupon':
                calculator = CouponDiscountDecorator(
                    calculator,
                    discount.get('code', ''),
                    discount.get('percentage', 0)
                )
            elif discount_type == 'bulk':
                calculator = BulkDiscountDecorator(
                    calculator,
                    discount.get('min_quantity', 0),
                    discount.get('percentage', 0)
                )
        
        return calculator