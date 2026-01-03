# backend/cart_singleton.py
from datetime import datetime
import json

class CartSingleton:
    """
    Singleton Pattern: Ensure only one cart manager instance exists
    This acts as a facade over your database cart operations
    """
    _instance = None
    _active_carts = {}  # Cache for active carts
    
    def __new__(cls):
        if cls._instance is None:
            print("🛒 Creating new CartSingleton instance...")
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the singleton"""
        self._active_carts = {}
        print("🛒 CartSingleton initialized")
    
    def get_cart_stats(self):
        """Get statistics about all carts (Singleton feature)"""
        return {
            'instance_id': id(self),
            'is_singleton': self._instance is not None,
            'active_carts_in_memory': len(self._active_carts),
            'description': 'Singleton Cart Manager - Only one instance in entire application'
        }
    
    def cache_cart(self, session_id, cart_data):
        """Cache cart data in memory (Singleton cache feature)"""
        self._active_carts[session_id] = {
            'data': cart_data,
            'last_accessed': datetime.now().isoformat()
        }
        print(f"🛒 Cached cart for session: {session_id}")
        return self._active_carts[session_id]
    
    def get_cached_cart(self, session_id):
        """Get cached cart if exists"""
        return self._active_carts.get(session_id)
    
    def clear_cart_cache(self, session_id=None):
        """Clear cart cache"""
        if session_id and session_id in self._active_carts:
            del self._active_carts[session_id]
            print(f"🛒 Cleared cache for session: {session_id}")
        elif session_id is None:
            self._active_carts.clear()
            print("🛒 Cleared all cart cache")
    
    def validate_cart(self, cart_data):
        """Validate cart data (Singleton business logic)"""
        if not cart_data:
            return False
        
        # Check if cart has items
        if 'items' not in cart_data:
            return False
        
        # Check if each item has required fields
        for item in cart_data.get('items', []):
            if not all(key in item for key in ['product_id', 'quantity']):
                return False
        
        return True
    
    def calculate_cart_totals(self, items):
        """Calculate cart totals (Singleton business logic)"""
        subtotal = 0
        item_count = 0
        
        for item in items:
            if 'product' in item and 'quantity' in item:
                price = item['product'].get('price', 0)
                quantity = item['quantity']
                subtotal += price * quantity
                item_count += quantity
        
        # Calculate shipping
        shipping = 0 if subtotal > 50 else 5.99
        
        # Calculate tax (8%)
        tax = subtotal * 0.08
        
        # Calculate total
        total = subtotal + shipping + tax
        
        return {
            'subtotal': round(subtotal, 2),
            'shipping': round(shipping, 2),
            'tax': round(tax, 2),
            'total': round(total, 2),
            'item_count': item_count
        }
    
    def get_cart_summary(self, cart_data):
        """Get formatted cart summary"""
        if not self.validate_cart(cart_data):
            return None
        
        totals = self.calculate_cart_totals(cart_data['items'])
        
        return {
            'summary': {
                'subtotal': totals['subtotal'],
                'shipping': totals['shipping'],
                'tax': totals['tax'],
                'total': totals['total'],
                'item_count': totals['item_count'],
                'shipping_info': 'Free shipping on orders over $50',
                'estimated_tax_rate': '8%'
            },
            'items': cart_data['items'],
            'session_id': cart_data.get('session_id', 'unknown')
        }
    
    def apply_discount(self, cart_data, discount_code):
        """Apply discount to cart (Singleton feature)"""
        discounts = {
            'WELCOME10': 0.10,  # 10% off
            'SAVE15': 0.15,     # 15% off
            'FREESHIP': 'free_shipping'
        }
        
        if discount_code not in discounts:
            return cart_data
        
        discount = discounts[discount_code]
        
        if discount == 'free_shipping':
            # Free shipping logic would be applied in calculate_cart_totals
            pass
        elif isinstance(discount, float):
            # Apply percentage discount
            if 'discounts' not in cart_data:
                cart_data['discounts'] = []
            
            cart_data['discounts'].append({
                'code': discount_code,
                'type': 'percentage',
                'value': discount * 100,
                'applied_at': datetime.now().isoformat()
            })
        
        return cart_data

# Global singleton instance
cart_manager = CartSingleton()