from flask import Flask, request, jsonify, session, redirect, url_for, render_template
from flask_cors import CORS
from cart_singleton import cart_manager
from database import get_db, init_db, get_db_session
from models import OrderItem, Order, Product, CartItem, User
from factories import ProductFactoryManager, ProductBuilder
from sqlalchemy import desc, asc, or_
from datetime import datetime
import random
import string
import json
from config import Config
from discount_decorators import DiscountFactory, BasePriceCalculator
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, func  # Add func here
from sqlalchemy import text  # Make sure to import text at the top of app.py
from functools import wraps


app = Flask(__name__, 
            static_folder='../frontend', 
            template_folder='templates')  # This is correct
app.config.from_object(Config)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'  # Add this
import os
from discount_decorators import (
    PriceCalculator, 
    BasePriceCalculator, 
    PercentageDiscountDecorator,
    FixedAmountDiscountDecorator,
    CouponDiscountDecorator,
    BulkDiscountDecorator,
    DiscountFactory
)
# In app.py, update CORS configuration
# In app.py, update the CORS configuration:
CORS(app, 
     origins=["http://localhost:8000", "http://localhost:5000", "http://127.0.0.1:8000", "http://127.0.0.1:5000", "null"],
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization', 'Accept', 'X-Requested-With', 'Origin'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
     expose_headers=['Content-Type', 'Authorization', 'Set-Cookie'],
     allow_credentials=True)
# Initialize database
init_db()

# Utility functionsf
def generate_order_number():
    """Generate unique order number"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"ORD-{timestamp}-{random_str}"
# Add this decorator function RIGHT AFTER YOUR IMPORTS, before your routes
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized', 'success': False}), 401
        
        # Check if user is admin
        db = get_db_session()
        try:
            user = db.query(User).filter(User.id == session['user_id']).first()
            if not user or user.role != 'admin':
                return jsonify({'error': 'Admin access required', 'success': False}), 403
        except Exception as e:
            return jsonify({'error': str(e), 'success': False}), 500
        finally:
            db.close()
        
        return f(*args, **kwargs)
    return decorated_function
# ==================== AUTHENTICATION ENDPOINTS ====================

@app.route('/api/login', methods=['POST'])
def login():
    """User login - FIXED VERSION"""
    db = None
    try:
        data = request.json
        login_input = data.get('username') or data.get('email')  # Accept both
        password = data.get('password')
        
        if not login_input or not password:
            return jsonify({'success': False, 'error': 'Username/Email and password required'}), 400
        
        db = get_db_session()
        # Find user by username OR email
        user = db.query(User).filter(
            (User.username == login_input) | (User.email == login_input)
        ).first()
        
        if user and user.check_password(password):
            # Store user info in session
            session['user_id'] = user.id
            session['username'] = user.username
            session['email'] = user.email
            session['role'] = user.role
            
            # Add CORS headers
            response = jsonify({
                'success': True,
                'message': 'Login successful',
                'user': user.to_dict()
            })
            
            return response, 200
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid username/email or password'
            }), 401
            
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        if db:
            db.close()

@app.route('/api/logout', methods=['POST'])
def logout():
    """User logout"""
    try:
        # Clear the session
        session.clear()
        
        response = jsonify({
            'success': True, 
            'message': 'Logged out successfully'
        })
        
        # Add CORS headers
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:8000')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        
        return response
    except Exception as e:
        print(f"Logout error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    try:
        if 'user_id' in session:
            return jsonify({
                'authenticated': True,
                'user': {
                    'id': session['user_id'],
                    'username': session.get('username'),
                    'email': session.get('email'),
                    'role': session.get('role')
                }
            })
        return jsonify({'authenticated': False})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/register', methods=['POST'])
def register():
    """Register new user"""
    db = None
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({'success': False, 'error': 'All fields are required'}), 400
        
        db = get_db_session()
        
        # Check if username or email already exists
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            return jsonify({
                'success': False,
                'error': 'Username or email already exists'
            }), 400
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            role='user'  # Default role
        )
        new_user.set_password(password)
        
        db.add(new_user)
        db.commit()
        
        # Auto login after registration
        session['user_id'] = new_user.id
        session['username'] = new_user.username
        session['email'] = new_user.email
        session['role'] = new_user.role
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        print(f"Registration error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        if db:
            db.close()

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users (admin only)"""
    db = None
    try:
        # Check if user is admin
        if session.get('role') != 'admin':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        db = get_db_session()
        users = db.query(User).all()
        
        return jsonify({
            'success': True,
            'users': [user.to_dict() for user in users]
        })
        
    except Exception as e:
        print(f"Get users error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        if db:
            db.close()

# ==================== FRONTEND ROUTES ====================

# ==================== FRONTEND ROUTES ====================

@app.route('/')
def index():
    """Serve main index page"""
    return render_template('index.html')  # This will now work!

@app.route('/login')
def login_page():
    """Serve login page"""
    return render_template('login.html')  # This will now work!

@app.route('/admin-dashboard')
def admin_dashboard():
    """Serve admin dashboard (admin only)"""
    if 'user_id' in session and session.get('role') == 'admin':
        return render_template('admin-dashboard.html')  # Fixed!
    return redirect('/login')
# ==================== ADMIN ENDPOINTS ====================

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    """Get admin dashboard statistics"""
    db = None
    try:
        # Check if user is admin
        if session.get('role') != 'admin':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        db = get_db_session()
        
        # Get counts
        total_products = db.query(Product).count()
        total_orders = db.query(Order).count()
        total_users = db.query(User).count()
        total_revenue = db.query(func.sum(Order.total_amount)).scalar() or 0
        
        # Get recent orders
        recent_orders = db.query(Order).order_by(Order.created_at.desc()).limit(10).all()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_products': total_products,
                'total_orders': total_orders,
                'total_users': total_users,
                'total_revenue': round(total_revenue, 2)
            },
            'recent_orders': [order.to_dict() for order in recent_orders]
        })
        
    except Exception as e:
        print(f"Admin stats error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        if db:
            db.close()

# ==================== EXISTING ENDPOINTS (keep all your existing endpoints below) ====================

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get products with filtering and pagination"""
    db = None
    try:
        db = get_db_session()
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 8))
        category = request.args.get('category')
        search = request.args.get('search')
        min_price = request.args.get('min_price')
        max_price = request.args.get('max_price')
        sort_by = request.args.get('sort_by', 'id')
        sort_order = request.args.get('sort_order', 'asc')
        
        query = db.query(Product)
        
        if category and category != 'all':
            query = query.filter(Product.category == category)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term)
                )
            )
        
        if min_price:
            query = query.filter(Product.price >= float(min_price))
        
        if max_price:
            query = query.filter(Product.price <= float(max_price))
        
        sort_column = {
            'price': Product.price,
            'rating': Product.rating,
            'reviews': Product.reviews,
            'name': Product.name
        }.get(sort_by, Product.id)
        
        if sort_order == 'desc':
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        total = query.count()
        offset = (page - 1) * per_page
        products = query.offset(offset).limit(per_page).all()
        
        result = jsonify({
            'success': True,
            'products': [p.to_dict() for p in products],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': (total + per_page - 1) // per_page
            }
        })
        
        return result
    
    except Exception as e:
        print(f"Error in get_products: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        if db:
            db.close()

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get single product by ID"""
    db = None
    try:
        db = get_db_session()
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        return jsonify({
            'success': True,
            'product': product.to_dict()
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.close()

@app.route('/api/products/categories', methods=['GET'])
def get_categories():
    """Get all product categories"""
    db = None
    try:
        db = get_db_session()
        categories = db.query(Product.category).distinct().all()
        return jsonify({
            'success': True,
            'categories': [c[0] for c in categories]
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.close()

# ==================== CART ENDPOINTS ====================

@app.route('/api/cart', methods=['GET'])
def get_cart():
    """Get cart items for session"""
    db = None
    try:
        session_id = request.args.get('session_id')
        print(f"🎯 DEBUG: Getting cart for session: {session_id}")
        
        if not session_id:
            return jsonify({'success': False, 'error': 'Session ID required'}), 400
        
        db = get_db_session()
        cart_items = db.query(CartItem).filter(
            CartItem.session_id == session_id
        ).all()
        
        print(f"🎯 DEBUG: Found {len(cart_items)} cart items")
        
        items_list = []
        total = 0
        
        for item in cart_items:
            item_dict = item.to_dict()
            items_list.append(item_dict)
            if item.product:
                total += item.product.price * item.quantity
        
        return jsonify({
            'success': True,
            'items': items_list,
            'total': round(total, 2),
            'count': len(cart_items)
        })
    
    except Exception as e:
        print(f"💥 ERROR in get_cart: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.close()

@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    """Add item to cart"""
    db = None
    try:
        data = request.json
        print(f"🎯 DEBUG: Received cart request: {data}")
        
        session_id = data.get('session_id')
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
        
        print(f"🎯 DEBUG: Parsed - session_id={session_id}, product_id={product_id}, quantity={quantity}")
        
        if not all([session_id, product_id]):
            print("❌ ERROR: Missing required fields")
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        db = get_db_session()
        print(f"🎯 DEBUG: Querying product id={product_id}")
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            print(f"❌ ERROR: Product {product_id} not found")
            # List available products for debugging
            all_products = db.query(Product.id, Product.name).all()
            print(f"📋 Available products: {all_products}")
            return jsonify({'success': False, 'error': f'Product {product_id} not found'}), 404
        
        print(f"✅ DEBUG: Found product: {product.name} (ID: {product.id})")
        
        # Check if item already exists in cart
        cart_item = db.query(CartItem).filter(
            CartItem.session_id == session_id,
            CartItem.product_id == product_id
        ).first()
        
        if cart_item:
            cart_item.quantity += quantity
            message = 'Cart item quantity updated'
            print(f"🔄 DEBUG: Updated existing cart item, new quantity: {cart_item.quantity}")
        else:
            cart_item = CartItem(
                session_id=session_id,
                product_id=product_id,
                quantity=quantity
            )
            db.add(cart_item)
            message = 'Item added to cart'
            print(f"🆕 DEBUG: Created new cart item")
        
        db.commit()
        print("✅ DEBUG: Database committed successfully")
        
        # Clear cache after update
        cart_manager.clear_cart_cache(session_id)
        
        return jsonify({
            "success": True,
            "message": "Item added to cart successfully"
        }), 200

    
    except Exception as e:
        print(f"💥 ERROR in add_to_cart: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.close()

@app.route('/api/cart/<int:item_id>', methods=['PUT'])
def update_cart_item(item_id):
    """Update cart item quantity"""
    db = None
    try:
        data = request.json
        quantity = data.get('quantity')
        
        if quantity is None or quantity < 0:
            return jsonify({'success': False, 'error': 'Invalid quantity'}), 400
        
        db = get_db_session()
        cart_item = db.query(CartItem).filter(CartItem.id == item_id).first()
        
        if not cart_item:
            return jsonify({'success': False, 'error': 'Cart item not found'}), 404
        
        if quantity == 0:
            db.delete(cart_item)
            message = 'Item removed from cart'
        else:
            cart_item.quantity = quantity
            message = 'Cart item updated'
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': message
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.close()

@app.route('/api/cart/<int:item_id>', methods=['DELETE'])
def remove_cart_item(item_id):
    """Remove item from cart"""
    db = None
    try:
        db = get_db_session()
        cart_item = db.query(CartItem).filter(CartItem.id == item_id).first()
        
        if not cart_item:
            return jsonify({'success': False, 'error': 'Cart item not found'}), 404
        
        db.delete(cart_item)
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Item removed from cart'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.close()

@app.route('/api/cart/clear', methods=['DELETE'])
def clear_cart():
    """Clear all items from cart for session"""
    db = None
    try:
        session_id = request.args.get('session_id')
        if not session_id:
            return jsonify({'success': False, 'error': 'Session ID required'}), 400
        
        db = get_db_session()
        db.query(CartItem).filter(CartItem.session_id == session_id).delete()
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Cart cleared'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.close()

# ==================== ORDER ENDPOINTS ====================
@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create a new order from cart with shipping info"""
    db = None
    try:
        print("DEBUG: Creating new order...")
        data = request.json
        session_id = data.get('session_id')
        shipping_info = data.get('shipping_info', {})
        
        if not session_id:
            return jsonify({'success': False, 'error': 'Session ID required'}), 400
        
        db = get_db_session()
        
        # Get cart items
        cart_items = db.query(CartItem).filter(
            CartItem.session_id == session_id
        ).all()
        
        if not cart_items:
            return jsonify({'success': False, 'error': 'Cart is empty'}), 400
        
        # Calculate total
        total = 0
        for item in cart_items:
            if item.product:
                total += item.product.price * item.quantity
        
        # Generate order number
        order_number = generate_order_number()
        
        # Get user_id if logged in
        user_id = session.get('user_id') if 'user_id' in session else None
        
        # Create the order
        order = Order(
            order_number=order_number,
            user_id=user_id,
            session_id=session_id,
            total_amount=total,
            status='confirmed',
            shipping_info=json.dumps(shipping_info)  # Save as JSON string
        )
        
        db.add(order)
        db.flush()  # Get the order ID
        print(f"DEBUG: Order created with ID: {order.id}")
        
        # Create order items
        for cart_item in cart_items:
            if cart_item.product:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=cart_item.product.id,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                db.add(order_item)
        
        # Clear the cart
        db.query(CartItem).filter(CartItem.session_id == session_id).delete()
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order created successfully',
            'order': {
                'id': order.id,
                'order_number': order.order_number,
                'total_amount': order.total_amount,
                'status': order.status
            }
        }), 201
    
    except Exception as e:
        print(f"Error creating order: {str(e)}")
        import traceback
        traceback.print_exc()
        if db:
            db.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.close()

@app.route('/api/orders/<order_number>', methods=['GET'])
def get_order(order_number):
    """Get order by order number"""
    db = None
    try:
        db = get_db_session()
        order = db.query(Order).filter(Order.order_number == order_number).first()
        
        if not order:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        return jsonify({
            'success': True,
            'order': order.to_dict()
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.close()

# ==================== DEBUG ENDPOINTS ====================

@app.route('/api/debug/products', methods=['GET'])
def debug_products():
    """Debug endpoint to list all products"""
    db = None
    try:
        db = get_db_session()
        products = db.query(Product).all()
        return jsonify({
            'success': True,
            'count': len(products),
            'products': [{
                'id': p.id,
                'name': p.name,
                'price': p.price,
                'category': p.category
            } for p in products]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.close()

@app.route('/api/debug/cart-items', methods=['GET'])
def debug_cart_items():
    """Debug endpoint to list all cart items"""
    db = None
    try:
        db = get_db_session()
        cart_items = db.query(CartItem).all()
        return jsonify({
            'success': True,
            'count': len(cart_items),
            'cart_items': [{
                'id': c.id,
                'session_id': c.session_id,
                'product_id': c.product_id,
                'quantity': c.quantity
            } for c in cart_items]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.close()

@app.route('/api/debug/test-cart', methods=['POST'])
def test_cart():
    """Test endpoint to add item to cart"""
    db = None
    try:
        test_data = {
            'session_id': 'test_session_' + str(int(datetime.now().timestamp())),
            'product_id': 1,
            'quantity': 1
        }
        
        print(f"🧪 TEST: Testing with data: {test_data}")
        
        db = get_db_session()
        # Check if product exists
        product = db.query(Product).filter(Product.id == test_data['product_id']).first()
        if not product:
            return jsonify({
                'success': False,
                'error': 'Product not found',
                'hint': 'Run /api/debug/products to see available products'
            }), 404
        
        # Add to cart
        cart_item = CartItem(
            session_id=test_data['session_id'],
            product_id=test_data['product_id'],
            quantity=test_data['quantity']
        )
        db.add(cart_item)
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Test cart item added',
            'test_data': test_data,
            'added_product': product.name
        })
    
    except Exception as e:
        print(f"💥 TEST ERROR: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.close()

# ==================== SINGLETON ENDPOINTS ====================

@app.route('/api/cart/singleton-stats', methods=['GET'])
def get_singleton_stats():
    """Get Singleton cart manager statistics"""
    try:
        stats = cart_manager.get_cart_stats()
        return jsonify({
            'success': True,
            'singleton_pattern': 'ACTIVE',
            'stats': stats,
            'description': 'Singleton Pattern: Only one CartManager instance exists'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

            
# ==================== DISCOUNT ENDPOINTS ====================

@app.route('/api/discounts/apply', methods=['POST'])
def apply_discounts():
    """Apply discounts to a product"""
    data = request.json
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    discounts = data.get('discounts', [])
    
    # Get product price from database
    # For now, use a mock price based on product_id
    product_price = 100  # Mock price
    
    # Calculate original price
    original_price = product_price * quantity
    
    # Create base calculator
    calculator = BasePriceCalculator()
    
    # Apply discounts in order
    for discount in discounts:
        discount_type = discount.get('type')
        
        if discount_type == 'percentage':
            calculator = PercentageDiscountDecorator(calculator, discount.get('percentage', 0))
        elif discount_type == 'fixed':
            calculator = FixedAmountDiscountDecorator(calculator, discount.get('amount', 0))
        elif discount_type == 'bulk':
            # Check if total cart quantity meets minimum
            # This should check actual cart total, not just this item quantity
            min_quantity = discount.get('min_quantity', 0)
            # We need to pass cart total quantity to properly check bulk
            # For now, we'll check this item's quantity
            if quantity >= min_quantity:
                calculator = PercentageDiscountDecorator(calculator, discount.get('percentage', 0))
        elif discount_type == 'coupon':
            # Handle coupon discount
            pass
    
    final_price = calculator.calculate_price(product_price, quantity)
    savings = original_price - final_price
    
    return jsonify({
        "product_id": product_id,
        "original_price": original_price,
        "final_price": final_price,
        "savings": savings,
        "discount_description": calculator.get_description()
    })
    
    
@app.route('/api/discounts/validate-coupon', methods=['POST'])
def validate_coupon():
    """Validate a coupon code"""
    data = request.json
    coupon_code = data.get('coupon_code', '').upper()
    
    valid_coupons = {
        "WELCOME20": {
            "type": "percentage",
            "percentage": 20,
            "description": "20% off your first purchase",
            "code": "WELCOME20"
        },
        "SAVE10": {
            "type": "fixed",
            "amount": 10,
            "description": "$10 off your order",
            "code": "SAVE10"
        },
        "SUMMER25": {
            "type": "percentage",
            "percentage": 25,
            "description": "25% off summer items",
            "code": "SUMMER25"
        }
    }
    
    if coupon_code in valid_coupons:
        return jsonify({
            "valid": True,
            "coupon": valid_coupons[coupon_code]
        })
    
    return jsonify({
        "valid": False,
        "message": "Invalid coupon code"
    })


@app.route('/api/discounts/active', methods=['GET'])
def get_active_discounts():
    """Get all active discounts"""
    active_discounts = [
        {
            "id": 1,
            "name": "Summer Sale",
            "type": "percentage",
            "value": 15,
            "description": "15% off on all summer items",
            "expires": "2024-08-31"
        },
        {
            "id": 2,
            "name": "First Purchase",
            "type": "fixed",
            "value": 10,
            "description": "$10 off your first order",
            "expires": "2024-12-31"
        },
        {
            "id": 3,
            "name": "Bulk Discount",
            "type": "percentage",
            "value": 20,
            "description": "Buy 3+ items and get 20% off",
            "min_quantity": 3,
            "expires": None
        },
        {
            "id": 4,
            "name": "Welcome Discount",
            "type": "percentage",
            "value": 20,
            "description": "20% off your first purchase",
            "expires": "2024-12-31"
        }
    ]
    return jsonify({"discounts": active_discounts})

# ==================== CREATE ADMIN USER ====================

@app.route('/api/create-admin', methods=['POST'])
def create_admin_user():
    """Create admin user (run this once)"""
    db = None
    try:
        data = request.json
        username = data.get('username', 'admin')
        email = data.get('email', 'admin@shopease.com')
        password = data.get('password', 'admin123')
        
        db = get_db_session()
        
        # Check if admin already exists
        admin = db.query(User).filter(
            (User.username == username) | (User.email == email) | (User.role == 'admin')
        ).first()
        
        if admin:
            return jsonify({
                'success': False,
                'message': 'Admin user already exists'
            }), 400
        
        # Create admin user
        admin_user = User(
            username=username,
            email=email,
            role='admin'
        )
        admin_user.set_password(password)
        
        db.add(admin_user)
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Admin user created successfully',
            'user': {
                'username': username,
                'email': email,
                'role': 'admin'
            }
        }), 201
        
    except Exception as e:
        print(f"Create admin error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        if db:
            db.close()

@app.route('/api/admin/products')
@admin_required
def get_all_products():
    """Get all products for admin management"""
    try:
        db = get_db_session()
        products = db.query(Product).order_by(Product.id).all()
        
        products_list = []
        for product in products:
            products_list.append({
                'id': product.id,
                'name': product.name,
                'category': product.category,
                'price': product.price,
                'rating': product.rating,
                'reviews': product.reviews,
                'description': product.description,
                'image': product.image,
                'created_at': product.created_at.isoformat() if product.created_at else None
            })
        
        return jsonify({
            'success': True,
            'products': products_list,
            'count': len(products_list)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
    finally:
        if db:
            db.close()

@app.route('/api/admin/products/<int:product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    """Delete a product"""
    try:
        db = get_db_session()
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404
        
        db.delete(product)
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Product deleted successfully'
        })
        
    except Exception as e:
        db.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
    finally:
        if db:
            db.close()
            
            
@app.route('/api/admin/products', methods=['POST'])
@admin_required
def create_product():
    """Create a new product"""
    db = None
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['name', 'category', 'price', 'description']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Check if product already exists
        db = get_db_session()
        existing_product = db.query(Product).filter(
            Product.name == data['name']
        ).first()
        
        if existing_product:
            return jsonify({
                'success': False,
                'error': 'Product with this name already exists'
            }), 400
        
        # Create new product
        new_product = Product(
            name=data['name'],
            category=data['category'],
            price=float(data['price']),
            description=data['description'],
            image=data.get('image', ''),
            rating=float(data.get('rating', 0)),
            reviews=int(data.get('reviews', 0))
        )
        
        db.add(new_product)
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Product created successfully',
            'product': {
                'id': new_product.id,
                'name': new_product.name,
                'category': new_product.category,
                'price': new_product.price,
                'description': new_product.description,
                'image': new_product.image,
                'rating': new_product.rating,
                'reviews': new_product.reviews,
                'created_at': new_product.created_at.isoformat() if new_product.created_at else None
            }
        }), 201
        
    except Exception as e:
        if db:
            db.rollback()
        print(f"Create product error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        if db:
            db.close()

@app.route('/api/admin/products/<int:product_id>', methods=['PUT'])
@admin_required
def update_product(product_id):
    """Update a product"""
    db = None
    try:
        data = request.json
        
        db = get_db_session()
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404
        
        # Update fields if provided
        if 'name' in data:
            # Check if new name already exists (excluding current product)
            existing = db.query(Product).filter(
                Product.name == data['name'],
                Product.id != product_id
            ).first()
            if existing:
                return jsonify({
                    'success': False,
                    'error': 'Another product with this name already exists'
                }), 400
            product.name = data['name']
        
        if 'category' in data:
            product.category = data['category']
        
        if 'price' in data:
            product.price = float(data['price'])
        
        if 'description' in data:
            product.description = data['description']
        
        if 'image' in data:
            product.image = data['image']
        
        if 'rating' in data:
            product.rating = float(data['rating'])
        
        if 'reviews' in data:
            product.reviews = int(data['reviews'])
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Product updated successfully',
            'product': {
                'id': product.id,
                'name': product.name,
                'category': product.category,
                'price': product.price,
                'description': product.description,
                'image': product.image,
                'rating': product.rating,
                'reviews': product.reviews
            }
        })
        
    except Exception as e:
        if db:
            db.rollback()
        print(f"Update product error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        if db:
            db.close()

@app.route('/api/categories', methods=['GET'])
def get_product_categories():
    """Get all product categories for dropdown"""
    db = None
    try:
        db = get_db_session()
        
        # Get distinct categories from existing products
        categories = db.query(Product.category).distinct().all()
        
        # Add some common categories if not present
        all_categories = [c[0] for c in categories if c[0]]
        common_categories = ['electronics', 'audio', 'wearables', 'mobile', 'gaming', 
                           'photography', 'makeup', 'nail-polish', 'clothing', 
                           'shoes', 'bags', 'jewelry']
        
        # Combine and remove duplicates
        combined = list(set(all_categories + common_categories))
        combined.sort()
        
        return jsonify({
            'success': True,
            'categories': combined
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        if db:
            db.close()


# ==================== ADMIN USER MANAGEMENT ENDPOINTS ====================

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def admin_get_users():
    """Get all users (admin only)"""
    db = None
    try:
        db = get_db_session()
        users = db.query(User).order_by(User.created_at.desc()).all()
        
        user_list = []
        for user in users:
            user_list.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
        
        return jsonify({
            'success': True,
            'users': user_list,
            'count': len(user_list)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
    finally:
        if db:
            db.close()

@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@admin_required
def admin_update_user(user_id):
    """Update user role (admin only)"""
    db = None
    try:
        data = request.json
        role = data.get('role')
        
        if not role or role not in ['user', 'admin']:
            return jsonify({
                'success': False,
                'error': 'Valid role (user/admin) required'
            }), 400
        
        db = get_db_session()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Don't allow self-demotion (admin changing their own role)
        if user.id == session.get('user_id') and role != 'admin':
            return jsonify({
                'success': False,
                'error': 'Cannot change your own admin role'
            }), 400
        
        user.role = role
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'User updated successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        })
        
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
    finally:
        if db:
            db.close()


@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def admin_delete_user(user_id):
    """Delete user (admin only) - DIRECT DELETE VERSION"""
    db = None
    try:
        db = get_db_session()
        
        # Don't allow self-deletion
        if user_id == session.get('user_id'):
            return jsonify({
                'success': False,
                'error': 'Cannot delete your own account'
            }), 400
        
        # First, check if user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Delete cart items associated with this user (optional, but good practice)
        try:
            db.query(CartItem).filter(
                CartItem.session_id.like(f'user_{user_id}_%')
            ).delete()
        except:
            pass  # If this fails, continue anyway
        
        # Use raw SQL with text() wrapper to avoid SQLAlchemy cascade issues
        result = db.execute(text("DELETE FROM users WHERE id = :user_id"), {"user_id": user_id})
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        })
        
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
    finally:
        if db:
            db.close()
            
@app.route('/api/admin/orders', methods=['GET'])
@admin_required
def get_all_orders():
    """Get all orders for admin dashboard"""
    db = None
    try:
        db = get_db_session()
        
        # Get all orders with their items
        orders = db.query(Order).order_by(Order.created_at.desc()).all()
        
        orders_list = []
        for order in orders:
            # Get order items
            order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
            
            # Get user info if available
            user_info = None
            if order.user_id:
                user = db.query(User).get(order.user_id)
                if user:
                    user_info = user.to_dict()
            
            orders_list.append({
                'id': order.id,
                'order_number': order.order_number,
                'user': user_info,
                'total_amount': order.total_amount,
                'status': order.status,
                'created_at': order.created_at.isoformat() if order.created_at else None,
                'item_count': len(order_items),
                'items': [{
                    'product_id': item.product_id,
                    'product_name': item.product.name if item.product else 'Unknown',
                    'quantity': item.quantity,
                    'price': item.price
                } for item in order_items]
            })
        
        return jsonify({
            'success': True,
            'orders': orders_list,
            'count': len(orders_list)
        })
        
    except Exception as e:
        print(f"Error getting orders: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.close()
        
        
@app.route('/api/admin/order-items', methods=['GET'])
@admin_required
def get_all_order_items():
    """Get all order items for admin dashboard"""
    db = None
    try:
        db = get_db_session()
        
        # Get all order items with product and order information
        order_items = db.query(OrderItem).order_by(OrderItem.created_at.desc()).all()
        
        order_items_list = []
        for item in order_items:
            # Get product info
            product = db.query(Product).get(item.product_id)
            
            # Get order info
            order = db.query(Order).get(item.order_id)
            
            order_items_list.append({
                'id': item.id,
                'order_id': item.order_id,
                'product_id': item.product_id,
                'quantity': item.quantity,
                'price': item.price,
                'created_at': item.created_at.isoformat() if item.created_at else None,
                'product': {
                    'name': product.name if product else None,
                    'image': product.image if product else None,
                    'price': product.price if product else None
                } if product else None,
                'order': {
                    'order_number': order.order_number if order else None,
                    'total_amount': order.total_amount if order else None
                } if order else None
            })
        
        return jsonify({
            'success': True,
            'order_items': order_items_list,
            'count': len(order_items_list)
        })
        
    except Exception as e:
        print(f"Error getting order items: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.close()  
            
            
# ==================== ANALYTICS ENDPOINTS ====================

@app.route('/api/admin/analytics/summary', methods=['GET'])
@admin_required
def get_analytics_summary():
    """Get analytics summary for dashboard"""
    db = None
    try:
        db = get_db_session()
        
        # Get period from query params
        period = request.args.get('period', '30')
        
        # Calculate date range
        from datetime import datetime, timedelta
        today = datetime.now()
        
        if period == '7':
            start_date = today - timedelta(days=7)
        elif period == '30':
            start_date = today - timedelta(days=30)
        elif period == '90':
            start_date = today - timedelta(days=90)
        elif period == '365':
            start_date = today - timedelta(days=365)
        else:
            start_date = None  # All time
        
        # Total revenue
        if start_date:
            total_revenue = db.query(func.sum(Order.total_amount)).filter(
                Order.created_at >= start_date
            ).scalar() or 0
            total_orders = db.query(func.count(Order.id)).filter(
                Order.created_at >= start_date
            ).scalar() or 0
        else:
            total_revenue = db.query(func.sum(Order.total_amount)).scalar() or 0
            total_orders = db.query(func.count(Order.id)).scalar() or 0
        
        # Average order value
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Get today's sales
        today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        today_revenue = db.query(func.sum(Order.total_amount)).filter(
            Order.created_at >= today_start
        ).scalar() or 0
        today_orders = db.query(func.count(Order.id)).filter(
            Order.created_at >= today_start
        ).scalar() or 0
        
        # Get yesterday's sales for comparison
        yesterday_start = today_start - timedelta(days=1)
        yesterday_end = today_start
        yesterday_revenue = db.query(func.sum(Order.total_amount)).filter(
            Order.created_at >= yesterday_start,
            Order.created_at < yesterday_end
        ).scalar() or 0
        
        # Calculate growth percentage
        revenue_growth = 0
        if yesterday_revenue > 0:
            revenue_growth = ((today_revenue - yesterday_revenue) / yesterday_revenue) * 100
        
        # Get top selling products
        top_products = db.query(
            OrderItem.product_id,
            Product.name,
            func.sum(OrderItem.quantity).label('total_quantity'),
            func.sum(OrderItem.price * OrderItem.quantity).label('total_revenue')
        ).join(Product, OrderItem.product_id == Product.id)\
         .group_by(OrderItem.product_id, Product.name)\
         .order_by(func.sum(OrderItem.quantity).desc())\
         .limit(5)\
         .all()
        
        # Get sales by category
        category_sales = db.query(
            Product.category,
            func.sum(OrderItem.quantity).label('total_quantity'),
            func.sum(OrderItem.price * OrderItem.quantity).label('total_revenue')
        ).join(Product, OrderItem.product_id == Product.id)\
         .group_by(Product.category)\
         .order_by(func.sum(OrderItem.price * OrderItem.quantity).desc())\
         .all()
        
        # Get recent orders for timeline
        recent_orders = db.query(Order).order_by(Order.created_at.desc()).limit(10).all()
        
        return jsonify({
            'success': True,
            'period': period,
            'summary': {
                'total_revenue': round(total_revenue, 2),
                'total_orders': total_orders,
                'avg_order_value': round(avg_order_value, 2),
                'today_revenue': round(today_revenue, 2),
                'today_orders': today_orders,
                'revenue_growth': round(revenue_growth, 2),
                'yesterday_revenue': round(yesterday_revenue, 2)
            },
            'top_products': [{
                'product_id': p[0],
                'name': p[1],
                'total_quantity': p[2] or 0,
                'total_revenue': float(p[3] or 0)
            } for p in top_products],
            'category_sales': [{
                'category': c[0] or 'Uncategorized',
                'total_quantity': c[1] or 0,
                'total_revenue': float(c[2] or 0)
            } for c in category_sales],
            'recent_orders': [order.to_dict() for order in recent_orders]
        })
        
    except Exception as e:
        print(f"Error getting analytics summary: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.close()

@app.route('/api/admin/analytics/sales-trend', methods=['GET'])
@admin_required
def get_sales_trend():
    """Get sales trend data for charts"""
    db = None
    try:
        db = get_db_session()
        
        period = request.args.get('period', '30')
        days = int(period)
        
        # Generate date range
        from datetime import datetime, timedelta
        today = datetime.now()
        start_date = today - timedelta(days=days)
        
        # Get daily sales data
        daily_sales = db.query(
            func.date(Order.created_at).label('date'),
            func.count(Order.id).label('order_count'),
            func.sum(Order.total_amount).label('revenue')
        ).filter(
            Order.created_at >= start_date
        ).group_by(
            func.date(Order.created_at)
        ).order_by(
            func.date(Order.created_at)
        ).all()
        
        # Format for chart
        dates = []
        orders_data = []
        revenue_data = []
        
        # Fill in missing dates
        current_date = start_date
        while current_date <= today:
            date_str = current_date.strftime('%Y-%m-%d')
            
            # Find sales for this date
            sales_data = next((s for s in daily_sales if s[0] == current_date.date()), None)
            
            dates.append(date_str)
            orders_data.append(sales_data[1] if sales_data else 0)
            revenue_data.append(float(sales_data[2]) if sales_data else 0)
            
            current_date += timedelta(days=1)
        
        return jsonify({
            'success': True,
            'labels': dates,
            'orders_data': orders_data,
            'revenue_data': revenue_data
        })
        
    except Exception as e:
        print(f"Error getting sales trend: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.close()

@app.route('/api/admin/analytics/hourly-sales', methods=['GET'])
@admin_required
def get_hourly_sales():
    """Get hourly sales data for today"""
    db = None
    try:
        db = get_db_session()
        
        # Get today's date
        from datetime import datetime, timedelta
        today = datetime.now()
        today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Get hourly sales
        hourly_sales = db.query(
            func.extract('hour', Order.created_at).label('hour'),
            func.count(Order.id).label('order_count'),
            func.sum(Order.total_amount).label('revenue')
        ).filter(
            Order.created_at >= today_start
        ).group_by(
            func.extract('hour', Order.created_at)
        ).order_by(
            func.extract('hour', Order.created_at)
        ).all()
        
        # Format for chart (24 hours)
        hours = list(range(24))
        hourly_orders = [0] * 24
        hourly_revenue = [0] * 24
        
        for sale in hourly_sales:
            hour = int(sale[0])
            hourly_orders[hour] = sale[1] or 0
            hourly_revenue[hour] = float(sale[2] or 0)
        
        # Format hour labels
        hour_labels = [f"{h:02d}:00" for h in hours]
        
        return jsonify({
            'success': True,
            'labels': hour_labels,
            'orders_data': hourly_orders,
            'revenue_data': hourly_revenue
        })
        
    except Exception as e:
        print(f"Error getting hourly sales: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.close()
if __name__ == '__main__':
    print("🚀 Starting Flask server...")
    print("📡 Server running on http://localhost:5000")
    print("🔗 Available endpoints:")
    print("   - GET  /api/health")
    print("   - POST /api/login")
    print("   - POST /api/register")
    print("   - POST /api/logout")
    print("   - GET  /api/check-auth")
    print("   - GET  /api/products")
    print("   - GET  /api/cart?session_id=YOUR_SESSION_ID")
    print("   - POST /api/cart")
    print("   - GET  /api/admin/stats (admin only)")
    print("   - POST /api/create-admin (create admin user)")
    app.run(debug=True, port=5000, host='0.0.0.0')