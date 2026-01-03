
class DiscountManager {
    constructor() {
        this.activeDiscounts = [];
        this.appliedDiscounts = [];
        this.cartItems = [];
        this.cartTotalQuantity = 0;
        this.init();
    }

    async init() {
        await this.loadActiveDiscounts();
        await this.loadCart();
        this.setupEventListeners();
    }

    async loadCart() {
        try {
            const sessionId = getSessionId();
            const response = await fetch(`${API_BASE_URL}/cart?session_id=${sessionId}`);
            const data = await response.json();
            
            if (data.success) {
                this.cartItems = data.items;
                this.cartTotalQuantity = this.calculateTotalQuantity();
                this.updateCartPrices();
            }
        } catch (error) {
            console.error('Error loading cart:', error);
        }
    }

    calculateTotalQuantity() {
        return this.cartItems.reduce((total, item) => total + item.quantity, 0);
    }

    async loadActiveDiscounts() {
        try {
            const response = await fetch(`${API_BASE_URL}/discounts/active`);
            const data = await response.json();
            
            if (data.discounts) {
                this.activeDiscounts = data.discounts;
                this.renderDiscounts();
            }
        } catch (error) {
            console.error('Error loading discounts:', error);
            // Fallback discounts
            this.activeDiscounts = [
                {
                    id: 1,
                    name: 'Summer Sale',
                    type: 'percentage',
                    value: 15,
                    description: '15% off on all summer items',
                    code: 'SUMMER15',
                    expires: '2024-08-31'
                },
                {
                    id: 2,
                    name: 'First Purchase',
                    type: 'fixed',
                    value: 10,
                    description: '$10 off your first order',
                    code: 'WELCOME10',
                    expires: '2024-12-31'
                },
                {
                    id: 3,
                    name: 'Bulk Discount',
                    type: 'bulk',
                    value: 20,
                    min_quantity: 3,
                    description: 'Buy 3+ items and get 20% off',
                    expires: null
                }
            ];
            this.renderDiscounts();
        }
    }

    renderDiscounts() {
        const container = document.getElementById('discountsContainer');
        if (!container) return;

        container.innerHTML = this.activeDiscounts.map(discount => {
            // Check if bulk discount is applicable
            const isBulkApplicable = discount.type === 'bulk' ? 
                this.cartTotalQuantity >= discount.min_quantity : true;
            
            // Check if already applied
            const isApplied = this.appliedDiscounts.some(d => d.id === discount.id);
            
            return `
            <div class="discount-card ${isApplied ? 'active' : ''}" data-discount-id="${discount.id}">
                <div class="discount-badge">
                    <i class="fas ${discount.type === 'percentage' ? 'fa-percentage' : 
                                    discount.type === 'fixed' ? 'fa-dollar-sign' : 
                                    'fa-boxes'}"></i>
                    ${discount.type === 'percentage' ? `${discount.value}%` : 
                     discount.type === 'fixed' ? `$${discount.value}` : 
                     `${discount.value}% off`}
                </div>
                <div class="discount-title">${discount.name}</div>
                <div class="discount-description">${discount.description}</div>
                ${discount.min_quantity ? `
                    <div class="discount-min-quantity ${isBulkApplicable ? 'applicable' : 'not-applicable'}">
                        <i class="fas ${isBulkApplicable ? 'fa-check-circle' : 'fa-info-circle'}"></i>
                        Requires ${discount.min_quantity}+ items in cart
                    </div>
                ` : ''}
                ${discount.expires ? `<div class="discount-expiry">Expires: ${discount.expires}</div>` : ''}
                <button class="apply-discount-btn ${isApplied ? 'applied' : ''} 
                    ${discount.type === 'bulk' && !isBulkApplicable ? 'disabled' : ''}"
                    onclick="discountManager.applyDiscount(${discount.id})"
                    ${discount.type === 'bulk' && !isBulkApplicable ? 'disabled' : ''}>
                    ${isApplied ? 
                        '<i class="fas fa-check"></i> Applied' : 
                        '<i class="fas fa-plus-circle"></i> Apply'}
                </button>
            </div>
            `;
        }).join('');
    }

    async applyDiscount(discountId) {
        const discount = this.activeDiscounts.find(d => d.id === discountId);
        if (!discount) return;

        // For bulk discount, check cart quantity
        if (discount.type === 'bulk') {
            if (this.cartTotalQuantity < discount.min_quantity) {
                this.showCouponMessage(`This discount requires ${discount.min_quantity} or more items in cart`, 'error');
                return;
            }
        }

        // Check if already applied
        if (this.appliedDiscounts.some(d => d.id === discount.id)) {
            this.showCouponMessage('Discount already applied!', 'info');
            return;
        }

        this.appliedDiscounts.push(discount);
        this.updateAppliedDiscounts();
        await this.updateCartPrices();
        
        // Update button state
        const discountCard = document.querySelector(`[data-discount-id="${discountId}"]`);
        if (discountCard) {
            const btn = discountCard.querySelector('.apply-discount-btn');
            btn.classList.add('applied');
            btn.innerHTML = '<i class="fas fa-check"></i> Applied';
            discountCard.classList.add('active');
        }
        
        this.showCouponMessage(`${discount.name} applied successfully!`, 'success');
        showNotification('Discount applied!');
    }

    async applyCoupon() {
        const couponCode = document.getElementById('couponCode').value.trim().toUpperCase();
        if (!couponCode) {
            this.showCouponMessage('Please enter a coupon code', 'error');
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/discounts/validate-coupon`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ coupon_code: couponCode })
            });

            const data = await response.json();
            
            if (data.valid) {
                // Check if coupon already applied
                if (this.appliedDiscounts.some(d => d.code === couponCode)) {
                    this.showCouponMessage('Coupon already applied!', 'info');
                    return;
                }

                // Create unique ID for coupon
                const couponId = `coupon_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
                
                // Add coupon to applied discounts
                this.appliedDiscounts.push({
                    id: couponId,
                    name: data.coupon.description || 'Coupon Discount',
                    type: data.coupon.type,
                    value: data.coupon.percentage || data.coupon.amount,
                    description: data.coupon.description,
                    code: couponCode,
                    discountData: data.coupon
                });
                
                this.updateAppliedDiscounts();
                await this.updateCartPrices();
                document.getElementById('couponCode').value = '';
                this.showCouponMessage('Coupon applied successfully!', 'success');
                showNotification('Coupon applied!');
            } else {
                this.showCouponMessage(data.message, 'error');
            }
        } catch (error) {
            console.error('Error applying coupon:', error);
            this.showCouponMessage('Error applying coupon', 'error');
        }
    }

    updateAppliedDiscounts() {
        const container = document.getElementById('appliedDiscountsList');
        if (!container) return;

        if (this.appliedDiscounts.length === 0) {
            container.innerHTML = '<p class="no-discounts">No discounts applied</p>';
            return;
        }

        container.innerHTML = this.appliedDiscounts.map(discount => {
            let valueText = '';
            if (discount.type === 'percentage') {
                valueText = `-${discount.value}%`;
            } else if (discount.type === 'fixed') {
                valueText = `-$${discount.value}`;
            } else if (discount.type === 'bulk') {
                valueText = `-${discount.value}%`;
            } else {
                valueText = discount.discountData ? 
                    `-${discount.discountData.percentage || discount.discountData.amount}${discount.discountData.percentage ? '%' : '$'}` : 
                    `-${discount.value}%`;
            }
            
            return `
            <div class="applied-discount-item" data-discount-id="${discount.id}">
                <span class="applied-discount-name">${discount.name}</span>
                <span class="applied-discount-value">${valueText}</span>
                <button class="remove-discount-btn" onclick="discountManager.removeDiscount('${discount.id}')">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            `;
        }).join('');
    }

    removeDiscount(discountId) {
        console.log('Removing discount:', discountId);
        console.log('Applied discounts before:', this.appliedDiscounts);
        
        // Filter out the discount
        this.appliedDiscounts = this.appliedDiscounts.filter(d => {
            console.log(`Comparing ${d.id} with ${discountId}:`, d.id.toString() !== discountId.toString());
            return d.id.toString() !== discountId.toString();
        });
        
        console.log('Applied discounts after:', this.appliedDiscounts);
        
        this.updateAppliedDiscounts();
        this.updateCartPrices();
        
        // Update discount card state for non-coupon discounts
        if (!discountId.toString().startsWith('coupon_')) {
            const discountCard = document.querySelector(`[data-discount-id="${discountId}"]`);
            if (discountCard) {
                const btn = discountCard.querySelector('.apply-discount-btn');
                btn.classList.remove('applied');
                btn.innerHTML = '<i class="fas fa-plus-circle"></i> Apply';
                discountCard.classList.remove('active');
            }
        }
        
        showNotification('Discount removed');
    }

    async updateCartPrices() {
        console.log('🔄 Updating cart prices with discounts...');
        
        // Update each cart item with discounts
        for (const cartItem of this.cartItems) {
            if (cartItem.product) {
                console.log(`🔄 Processing: ${cartItem.product.name}, Qty: ${cartItem.quantity}`);
                const discountedPrice = await this.calculateDiscountedPrice(
                    cartItem.product.id, 
                    cartItem.quantity
                );
                
                // Update the cart item display
                this.updateCartItemDisplay(cartItem.id, cartItem.product.price, discountedPrice, cartItem.quantity);
            }
        }
        
        // Update cart summary
        await this.updateCartSummary();
    }

    async calculateDiscountedPrice(productId, quantity) {
        try {
            console.log(`🔍 Calculating discount for product ${productId}, quantity ${quantity}`);
            console.log(`🔍 Applied discounts:`, this.appliedDiscounts);
            
            // Prepare discounts data for API
            const discountsData = this.appliedDiscounts.map(d => {
                const discountObj = {
                    type: d.type,
                    code: d.code || null
                };
                
                if (d.type === 'percentage') {
                    discountObj.percentage = d.value;
                } else if (d.type === 'fixed') {
                    discountObj.amount = d.value;
                } else if (d.type === 'bulk') {
                    discountObj.percentage = d.value;
                    discountObj.min_quantity = d.min_quantity;
                    // Include total cart quantity for bulk discount validation
                    discountObj.cart_total_quantity = this.cartTotalQuantity;
                } else if (d.discountData) {
                    // For coupon discounts
                    discountObj.type = d.discountData.type;
                    if (d.discountData.percentage) {
                        discountObj.percentage = d.discountData.percentage;
                    }
                    if (d.discountData.amount) {
                        discountObj.amount = d.discountData.amount;
                    }
                }
                
                return discountObj;
            });
            
            const response = await fetch(`${API_BASE_URL}/discounts/apply`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    product_id: productId,
                    quantity: quantity,
                    discounts: discountsData
                })
            });

            const data = await response.json();
            console.log(`🔍 Discount API response:`, data);
            
            if (data && data.final_price !== undefined) {
                return data.final_price;
            }
            
            return null;
        } catch (error) {
            console.error('❌ Error calculating discount:', error);
            return null;
        }
    }


    async updateCartTotal() {
        // Calculate total from all cart items
        let total = 0;
        let totalSavings = 0;
        
        const cartItems = document.querySelectorAll('.cart-item');
        for (const item of cartItems) {
            const priceElement = item.querySelector('.discounted-price');
            if (priceElement) {
                total += parseFloat(priceElement.textContent.replace('$', ''));
                
                const originalPrice = item.querySelector('.original-price');
                if (originalPrice) {
                    const original = parseFloat(originalPrice.textContent.replace('$', ''));
                    const discounted = parseFloat(priceElement.textContent.replace('$', ''));
                    totalSavings += original - discounted;
                }
            }
        }
        
        // Update total display
        const totalElement = document.querySelector('.cart-total .total-amount');
        if (totalElement) {
            totalElement.textContent = `$${total.toFixed(2)}`;
        }
        
        // Update savings display
        const savingsElement = document.querySelector('.total-savings');
        if (savingsElement) {
            savingsElement.innerHTML = totalSavings > 0 
                ? `<i class="fas fa-piggy-bank"></i> You save: <span class="savings-amount">$${totalSavings.toFixed(2)}</span>`
                : '';
        }
    }

    showMessage(message, type = 'info') {
        const messageDiv = document.getElementById('couponMessage');
        if (messageDiv) {
            messageDiv.textContent = message;
            messageDiv.className = `coupon-message ${type}`;
            
            setTimeout(() => {
                messageDiv.textContent = '';
                messageDiv.className = 'coupon-message';
            }, 3000);
        }
    }

    setupEventListeners() {
        // Global discount toggle
        document.addEventListener('DOMContentLoaded', () => {
            const discountToggle = document.createElement('button');
            discountToggle.className = 'discount-toggle-btn';
            discountToggle.innerHTML = '<i class="fas fa-tag"></i> Show Discounts';
            discountToggle.onclick = () => this.toggleDiscountsPanel();
            
            document.querySelector('.cart-actions')?.appendChild(discountToggle);
        });
    }

    toggleDiscountsPanel() {
        const panel = document.querySelector('.discounts-panel');
        if (panel) {
            panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
        }
    }
}

// Initialize discount manager
const discountManager = new DiscountManager();