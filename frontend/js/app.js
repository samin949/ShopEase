// API Configuration
class API {
    constructor() {
        this.baseURL = 'http://localhost:5000/api';
        this.sessionId = this.getSessionId();
    }
    
    getSessionId() {
        let sessionId = localStorage.getItem('shopease_session_id');
        if (!sessionId) {
            sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('shopease_session_id', sessionId);
        }
        return sessionId;
    }
    
async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;

    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    const config = { ...defaultOptions, ...options };

    try {
        const response = await fetch(url, config);

        let data;
        try {
            data = await response.json();
        } catch (e) {
            console.warn("⚠ JSON parsing failed. Response was not valid JSON.");
            data = {}; // Prevents the popup error
        }

        if (!response.ok) {
            throw new Error(data.error || `HTTP error: ${response.status}`);
        }

        return data;

    } catch (error) {
        console.error("API request failed:", error);
        throw error;
    }
}


      
    // Products
    async getProducts(filters = {}) {
        const params = new URLSearchParams();
        
        Object.keys(filters).forEach(key => {
            if (filters[key] !== undefined && filters[key] !== null) {
                params.append(key, filters[key]);
            }
        });
        
        return this.request(`/products?${params}`);
    }
    
    async getProduct(productId) {
        return this.request(`/products/${productId}`);
    }
    
    async getCategories() {
        return this.request('/products/categories');
    }
    
    // Singleton Pattern features
    async getCartSingletonStats() {
        return this.request('/cart/singleton-stats');
    }
    
    async applyDiscount(discountCode) {
        return this.request('/cart/apply-discount', {
            method: 'POST',
            body: JSON.stringify({
                session_id: this.sessionId,
                discount_code: discountCode
            })
        });
    }
    
    // Cart
    async getCart() {
        return this.request(`/cart?session_id=${this.sessionId}`);
    }
    
    async addToCart(productId, quantity = 1) {
        return this.request('/cart', {
            method: 'POST',
            body: JSON.stringify({
                product_id: productId,
                session_id: this.sessionId,
                quantity: quantity
            })
        });
    }
    
    async updateCartItem(itemId, quantity) {
        return this.request(`/cart/${itemId}`, {
            method: 'PUT',
            body: JSON.stringify({ quantity })
        });
    }
    
    async removeFromCart(itemId) {
        return this.request(`/cart/${itemId}`, {
            method: 'DELETE'
        });
    }
    
    async clearCart() {
        return this.request(`/cart/clear?session_id=${this.sessionId}`, {
            method: 'DELETE'
        });
    }
    
    // Orders
    async createOrder(shippingInfo) {
    return this.request('/orders', {
        method: 'POST',
        body: JSON.stringify({
            session_id: this.sessionId,
            shipping_info: shippingInfo
        })
    });
}

    
    async getOrder(orderNumber) {
        return this.request(`/orders/${orderNumber}`);
    }
    
    // Health check
    async healthCheck() {
        return this.request('/health');
    }
}

// Create global API instance
const api = new API();

// Utility functions
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            <span>${message}</span>
            <button class="notification-close">&times;</button>
        </div>
    `;
    
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${type === 'success' ? '#2ecc71' : '#e74c3c'};
        color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        animation: slideInRight 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        notification.remove();
    });
    
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

function generateStars(rating) {
    let stars = '';
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;
    
    for (let i = 0; i < fullStars; i++) {
        stars += '<i class="fas fa-star"></i>';
    }
    
    if (hasHalfStar) {
        stars += '<i class="fas fa-star-half-alt"></i>';
    }
    
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
    for (let i = 0; i < emptyStars; i++) {
        stars += '<i class="far fa-star"></i>';
    }
    
    return stars;
}

// Format price
function formatPrice(price) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(price);
}

// Cart functionality
async function fetchCart() {
    try {
        const response = await api.getCart();
        console.log('📦 Cart response:', response);  // Add this line to debug
        
        const cartItemsContainer = document.getElementById('cartItems');
        const cartSummaryContainer = document.getElementById('cartSummary');
        
        if (response.success) {
            // FIX HERE: Use response.items (plural) instead of response.items
            const cartItems = response.items || [];
            
            if (cartItems.length > 0) {
                // Render cart items
                renderCartItems(cartItems);
                
                // Render cart summary
                renderCartSummary(response);
            } else {
                showEmptyCart();
            }
        } else {
            showEmptyCart();
        }
    } catch (error) {
        console.error('Error fetching cart:', error);
        showEmptyCart();
    }
}

function renderCartItems(items) {
    const cartItemsContainer = document.getElementById('cartItems');
    if (!cartItemsContainer) return;
    
    cartItemsContainer.innerHTML = '';
    
    items.forEach(item => {
        const cartItem = document.createElement('div');
        cartItem.className = 'cart-item';
        
        // Check if product data exists
        const product = item.product || {};
        const itemTotal = product.price ? product.price * item.quantity : 0;
        
        cartItem.innerHTML = `
            <div class="cart-item-image">
                <img src="${product.image_url || 'images/placeholder.jpg'}" alt="${product.name || 'Product'}" 
                     onerror="this.src='images/placeholder.jpg'">
            </div>
            <div class="cart-item-details">
                <h3 class="cart-item-name">${product.name || 'Product'}</h3>
                <div class="cart-item-category">${product.category || 'Category'}</div>
                <div class="cart-item-price">$${product.price ? product.price.toFixed(2) : '0.00'}</div>
                <div class="cart-item-controls">
                    <div class="quantity-controls">
                        <button class="quantity-btn" onclick="updateCartItemQuantity(${item.id}, ${item.quantity - 1})">
                            <i class="fas fa-minus"></i>
                        </button>
                        <span class="quantity">${item.quantity}</span>
                        <button class="quantity-btn" onclick="updateCartItemQuantity(${item.id}, ${item.quantity + 1})">
                            <i class="fas fa-plus"></i>
                        </button>
                    </div>
                    <button class="remove-btn" onclick="removeCartItem(${item.id})">
                        <i class="fas fa-trash"></i>
                        Remove
                    </button>
                </div>
            </div>
        `;
        cartItemsContainer.appendChild(cartItem);
    });
}

function renderCartSummary(cartData) {
    const cartSummary = document.getElementById('cartSummary');
    if (!cartSummary) return;
    
    // Calculate totals
    const subtotal = cartData.total || 0;  // Backend returns 'total'
    const shipping = subtotal > 50 ? 0 : 5.99;
    const tax = subtotal * 0.08;
    const total = subtotal + shipping + tax;
    const itemCount = cartData.count || cartData.items?.length || 0;  // Backend returns 'count'
    
    cartSummary.innerHTML = `
        <h3 class="summary-title">Order Summary</h3>
        <div class="summary-row">
            <span class="summary-label">Items (${itemCount})</span>
            <span class="summary-value">$${subtotal.toFixed(2)}</span>
        </div>
        <div class="summary-row">
            <span class="summary-label">Shipping</span>
            <span class="summary-value">${shipping === 0 ? 'Free' : '$' + shipping.toFixed(2)}</span>
        </div>
        <div class="summary-row">
            <span class="summary-label">Tax</span>
            <span class="summary-value">$${tax.toFixed(2)}</span>
        </div>
        <div class="summary-row">
            <span class="summary-label">Total</span>
            <span class="summary-value">$${total.toFixed(2)}</span>
        </div>
        <div id="discountSection"></div>
        <button class="checkout-btn" onclick="goToCheckout()">
            <i class="fas fa-lock"></i>
            Proceed to Checkout
        </button>
    `;
    
    // Add discount section
    addDiscountFunctionality();
}

function showEmptyCart() {
    const cartItemsContainer = document.getElementById('cartItems');
    const cartSummary = document.getElementById('cartSummary');
    
    if (cartItemsContainer) {
        cartItemsContainer.innerHTML = `
            <div class="empty-cart">
                <div class="empty-cart-icon">
                    <i class="fas fa-shopping-cart"></i>
                </div>
                <h3>Your cart is empty</h3>
                <p>Looks like you haven't added any items to your cart yet.</p>
                <a href="products.html" class="continue-shopping">
                    <i class="fas fa-shopping-bag"></i>
                    Continue Shopping
                </a>
            </div>
        `;
    }
    
    if (cartSummary) {
        cartSummary.innerHTML = '';
    }
}

async function updateCartItemQuantity(itemId, newQuantity) {
    try {
        if (newQuantity <= 0) {
            await removeCartItem(itemId);
            return;
        }
        
        await api.updateCartItem(itemId, newQuantity);
        showNotification('Cart updated successfully');
        fetchCart();
    } catch (error) {
        console.error('Error updating cart item:', error);
        showNotification('Failed to update cart', 'error');
    }
}

async function removeCartItem(itemId) {
    try {
        await api.removeFromCart(itemId);
        showNotification('Item removed from cart');
        fetchCart();
    } catch (error) {
        console.error('Error removing cart item:', error);
        showNotification('Failed to remove item', 'error');
    }
}

function goToCheckout() {
    window.location.href = 'checkout.html';
}

// Singleton Pattern functions
function demonstrateSingletonPattern() {
    console.log("=== SINGLETON PATTERN DEMONSTRATION ===");
    console.log("The Cart Manager uses Singleton Pattern which means:");
    console.log("1. Only ONE instance of CartManager exists in the entire application");
    console.log("2. All cart operations go through this single instance");
    console.log("3. Cart cache and validation logic is centralized");
    console.log("4. Memory efficient - no duplicate cart managers");
    
    // Check Singleton status
    api.getCartSingletonStats()
        .then(data => {
            if (data.success) {
                console.log("✅ Singleton Pattern is ACTIVE");
                console.log("Singleton Stats:", data.stats);
                
                // Show notification about Singleton
                showSingletonNotification();
            }
        })
        .catch(error => {
            console.log("Singleton check failed:", error);
        });
}

function showSingletonNotification() {
    const notification = document.createElement('div');
    notification.className = 'singleton-notification';
    notification.innerHTML = `
        <div class="singleton-content">
            <div class="singleton-icon">🛒</div>
            <div class="singleton-text">
                <strong>Singleton Pattern Active</strong>
                <p>Cart is managed by a single instance across the entire app</p>
            </div>
            <button class="singleton-close">&times;</button>
        </div>
    `;
    
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideInUp 0.5s ease;
        max-width: 300px;
        border-left: 4px solid #46F0D2;
    `;
    
    document.body.appendChild(notification);
    
    // Add styles for slide animation
    if (!document.querySelector('#singleton-styles')) {
        const style = document.createElement('style');
        style.id = 'singleton-styles';
        style.textContent = `
            @keyframes slideInUp {
                from {
                    transform: translateY(100%);
                    opacity: 0;
                }
                to {
                    transform: translateY(0);
                    opacity: 1;
                }
            }
            .singleton-content {
                display: flex;
                align-items: center;
                gap: 1rem;
            }
            .singleton-icon {
                font-size: 1.5rem;
            }
            .singleton-text {
                flex: 1;
            }
            .singleton-text strong {
                display: block;
                margin-bottom: 0.25rem;
            }
            .singleton-text p {
                margin: 0;
                font-size: 0.9rem;
                opacity: 0.9;
            }
            .singleton-close {
                background: none;
                border: none;
                color: white;
                font-size: 1.5rem;
                cursor: pointer;
                padding: 0;
                line-height: 1;
            }
        `;
        document.head.appendChild(style);
    }
    
    // Close button
    const closeBtn = notification.querySelector('.singleton-close');
    closeBtn.addEventListener('click', () => {
        notification.remove();
    });
    
    // Auto remove after 10 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 10000);
}

// Add discount functionality to cart.html
function addDiscountFunctionality() {
    const discountSection = document.getElementById('discountSection');
    if (!discountSection) return;
    
    discountSection.innerHTML = `
        <div class="discount-container">
            <h4><i class="fas fa-tag"></i> Apply Discount Code</h4>
            <div class="discount-input-group">
                <input type="text" id="discountCode" placeholder="Enter discount code">
                <button onclick="applyDiscount()" class="discount-btn">
                    <i class="fas fa-check"></i> Apply
                </button>
            </div>
            <div class="discount-codes">
                <small>Try: WELCOME10 (10% off) | SAVE15 (15% off) | FREESHIP (Free Shipping)</small>
            </div>
        </div>
    `;
}

async function applyDiscount() {
    const discountCode = document.getElementById('discountCode')?.value;
    if (!discountCode) {
        showNotification('Please enter a discount code', 'error');
        return;
    }
    
    try {
        const result = await api.applyDiscount(discountCode);
        if (result.success) {
            showNotification(`Discount ${discountCode} applied successfully!`, 'success');
            // Refresh cart to show updated totals
            fetchCart();
        } else {
            showNotification('Invalid discount code', 'error');
        }
    } catch (error) {
        showNotification('Failed to apply discount', 'error');
    }
}

// Add CSS for discount section
function addDiscountCSS() {
    if (!document.querySelector('#discount-css')) {
        const style = document.createElement('style');
        style.id = 'discount-css';
        style.textContent = `
            .discount-container {
                margin: 20px 0;
                padding: 15px;
                background: rgba(70, 240, 210, 0.1);
                border-radius: 10px;
                border: 1px solid rgba(70, 240, 210, 0.3);
            }
            
            .discount-container h4 {
                margin-bottom: 10px;
                color: #46F0D2;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .discount-input-group {
                display: flex;
                gap: 10px;
                margin-bottom: 10px;
            }
            
            #discountCode {
                flex: 1;
                padding: 10px 15px;
                border: 1px solid var(--border);
                border-radius: 8px;
                background: var(--bg);
                color: var(--text);
                font-size: 1rem;
            }
            
            .discount-btn {
                padding: 10px 20px;
                background: #46F0D2;
                color: #131321;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 8px;
                transition: all 0.3s ease;
            }
            
            .discount-btn:hover {
                background: #36E0C2;
                transform: translateY(-2px);
            }
            
            .discount-codes small {
                color: var(--text);
                opacity: 0.7;
                font-size: 0.85rem;
            }
        `;
        document.head.appendChild(style);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Add discount CSS
    addDiscountCSS();
    
    // Initialize cart if on cart page
    if (window.location.pathname.includes('cart.html')) {
        fetchCart();
        
        // Add Singleton demonstration
        demonstrateSingletonPattern();
    }
    
    // Add theme toggle functionality
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            if (document.body.classList.contains("light")) {
                document.body.classList.remove("light");
                document.body.classList.add("dark");
                themeToggle.textContent = "Light Mode";
            } else {
                document.body.classList.remove("dark");
                document.body.classList.add("light");
                themeToggle.textContent = "Dark Mode";
            }
        });
    }
});

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { 
        api, 
        showNotification, 
        generateStars, 
        formatPrice,
        fetchCart,
        updateCartItemQuantity,
        removeCartItem,
        demonstrateSingletonPattern,
        applyDiscount
    };
}