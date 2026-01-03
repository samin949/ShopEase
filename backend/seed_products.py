import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from models import Product
from app import app
from database import SessionLocal
from factories import ProductFactoryManager, ProductBuilder
import json

def seed_products():
    """Seed database with sample products from your frontend data"""
    
    # Your products data from frontend
    products_data = [
           {

        "name": "UltraSlim Pro Laptop",
        "category": "electronics",
        "price": 1299.99,
        "rating": 4.5,
        "reviews": 128,
        "description": "Powerful performance in a sleek, lightweight design with all-day battery life.",
        "image": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8bGFwdG9wfGVufDB8fDB8fHww&auto=format&fit=crop&w=500&q=60",
        
    },
    {
        
        "name": "NoiseCancel Pro Headphones",
        "category": "audio",
        "price": 349.99,
        "rating": 5.0,
        "reviews": 64,
        "description": "Immersive sound experience with advanced noise cancellation technology.",
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8aGVhZHBob25lc3xlbnwwfHwwfHx8MA%3D%3D&auto=format&fit=crop&w=500&q=60",
       
    },
    {
    
        "name": "FitTrack Smartwatch",
        "category": "wearables",
        "price": 199.99,
        "rating": 4.0,
        "reviews": 92,
        "description": "Track your fitness, monitor health metrics, and stay connected on the go.",
        "image": "https://images.unsplash.com/photo-1546868871-7041f2a55e12?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8c21hcnR3YXRjaHxlbnwwfHwwfHx8MA%3D%3D&auto=format&fit=crop&w=500&q=60",
       
    },
    {
        
        "name": "ProShot DSLR Camera",
        "category": "photography",
        "price": 899.99,
        "rating": 4.5,
        "reviews": 76,
        "description": "Capture stunning photos with professional-grade camera and lenses.",
        "image": "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8Y2FtZXJhfGVufDB8fDB8fHww&auto=format&fit=crop&w=500&q=60",
       
    },
    {
    
        "name": "UltraPhone Pro",
        "category": "mobile",
        "price": 999.99,
        "rating": 5.0,
        "reviews": 203,
        "description": "Next-gen smartphone with advanced camera and lightning-fast performance.",
        "image": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8c21hcnRwaG9uZXxlbnwwfHwwfHx8MA%3D%3D&auto=format&fit=crop&w=500&q=60",
        
    },
    {
        
        "name": "GameMax Console",
        "category": "gaming",
        "price": 499.99,
        "rating": 4.7,
        "reviews": 156,
        "description": "Ultimate gaming experience with 4K graphics and immersive gameplay.",
        "image": "https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8Z2FtaW5nJTIwY29uc29sZXxlbnwwfHwwfHx8MA%3D%3D&auto=format&fit=crop&w=500&q=60",
       
    },
    {
      
        "name": "Ear buds pro",
        "category": "audio",
        "price": 179.99,
        "rating": 4.3,
        "reviews": 89,
        "description": "True wireless earbuds with crystal clear sound and comfortable fit.",
        "image": "https://images.unsplash.com/photo-1572569511254-d8f925fe2cbb?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8ZWFyYnVkc3xlbnwwfHwwfHx8MA%3D%3D&auto=format&fit=crop&w=500&q=60",
        
    },
    {
        "id": 8,
        "name": "Tablet Pro Max",
        "category": "electronics",
        "price": 749.99,
        "rating": 4.6,
        "reviews": 112,
        "description": "Versatile tablet with powerful performance and stunning display.",
        "image": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8dGFibGV0fGVufDB8fDB8fHww&auto=format&fit=crop&w=500&q=60",
        
    },
    {
    
        "name": "Gaming Keyboard",
        "category": "gaming",
        "price": 129.99,
        "rating": 4.4,
        "reviews": 67,
        "description": "Mechanical gaming keyboard with RGB lighting and programmable keys.",
        "image": "https://images.unsplash.com/photo-1541140532154-b024d705b90a?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8Z2FtaW5nJTIwa2V5Ym9hcmR8ZW58MHx8MHx8fDA%3D%3D&auto=format&fit=crop&w=500&q=60",
        
    },
    {
  
        "name": "Smart Home Hub",
        "category": "electronics",
        "price": 199.99,
        "rating": 4.2,
        "reviews": 54,
        "description": "Central control for your smart home devices with voice assistant.",
        "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTaKwWgK77kL9bkqiLsX1FRmQGCtNKFhugWaA&s",
       
    },
    {
     
        "name": "Fitness Tracker",
        "category": "wearables",
        "price": 79.99,
        "rating": 4.1,
        "reviews": 143,
        "description": "Track steps, calories, sleep, and heart rate with this sleek fitness band.",
        "image": "https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8Zml0bmVzcyUyMHRyYWNrZXJ8ZW58MHx8MHx8fDA%3D&auto=format&fit=crop&w=500&q=60",

        "specifications": {
            "Display": "1.1\" AMOLED",
            "Battery Life": "14 days",
            "Water Resistance": "5 ATM",
            "Sensors": "Heart rate, SpO2, Sleep",
            "Compatibility": "iOS & Android"
        },
        
    },
    {
       
        "name": "Portable Speaker",
        "category": "audio",
        "price": 129.99,
        "rating": 4.5,
        "reviews": 98,
        "description": "Waterproof portable speaker with 360-degree sound and long battery life.",
        "image": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8c3BlYWtlcnxlbnwwfHwwfHx8MA%3D%3D&auto=format&fit=crop&w=500&q=60",

    },
    {
     
        "name": "4K Monitor",
        "category": "electronics",
        "price": 399.99,
        "rating": 4.6,
        "reviews": 87,
        "description": "Crystal clear 4K display with HDR support and ultra-thin bezels.",
        "image": "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8bW9uaXRvcnxlbnwwfHwwfHx8MA%3D%3D&auto=format&fit=crop&w=500&q=60",
        "store": {
            "id": 1,
            "name": "Tech Galaxy",
            "rating": 4.7,
            "products": 234
        },
       
    },
    {
        
        "name": "Wireless Mouse",
        "category": "electronics",
        "price": 59.99,
        "rating": 4.3,
        "reviews": 234,
        "description": "Ergonomic wireless mouse with precision tracking and long battery life.",
        "image": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8bW91c2V8ZW58MHx8MHx8fDA%3D&auto=format&fit=crop&w=500&q=60",
       
     
    },
    {
        "name": "Bluetooth Speaker",
        "category": "audio",
        "price": 89.99,
        "rating": 4.2,
        "reviews": 156,
        "description": "Compact Bluetooth speaker with impressive sound quality and bass.",
        "image": "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8Ymx1ZXRvb3RoJTIwc3BlYWtlcnxlbnwwfHwwfHx8MA%3D%3D&auto=format&fit=crop&w=500&q=60",


    },
    {
        
        "name": "Gaming Chair",
        "category": "gaming",
        "price": 299.99,
        "rating": 4.4,
        "reviews": 189,
        "description": "Ergonomic gaming chair with lumbar support and adjustable features.",
        "image": "https://images.unsplash.com/photo-1701937189004-cbf07aed8186?q=80&w=765&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",

    },
    {
   
        "name": "External Hard Drive",
        "category": "electronics",
        "price": 129.99,
        "rating": 4.5,
        "reviews": 203,
        "description": "High-speed external hard drive with massive storage capacity.",
        "image": "https://plus.unsplash.com/premium_photo-1761494495055-6077392f40a4?q=80&w=1171&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
      
       
    },
    {
        
        "name": "Webcam Pro",
        "category": "electronics",
        "price": 79.99,
        "rating": 4.1,
        "reviews": 145,
        "description": "HD webcam with autofocus and built-in microphone for crystal clear video calls.",
        "image": "https://images.unsplash.com/photo-1626581795188-8efb9a00eeec?q=80&w=735&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    
        
    },
    {
        
        "name": "Wireless Charger",
        "category": "electronics",
        "price": 39.99,
        "rating": 4.0,
        "reviews": 278,
        "description": "Fast wireless charging pad compatible with all Qi-enabled devices.",
        "image": "https://images.unsplash.com/photo-1615526675159-e248c3021d3f?q=80&w=686&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",

    
    },
    {
      
        "name": "VR Headset",
        "category": "gaming",
        "price": 399.99,
        "rating": 4.3,
        "reviews": 92,
        "description": "Immersive virtual reality headset with high-resolution displays.",
        "image": "https://images.unsplash.com/photo-1702471897393-47ec1ba1192b?q=80&w=740&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",

       
    },
    {
       
        "name": "Matte Liquid Lipstick Set",
        "category": "makeup",
        "price": 34.99,
        "rating": 4.7,
        "reviews": 289,
        "description": "Long-lasting matte liquid lipstick in 6 trendy shades, transfer-proof formula.",
        "image": "https://images.unsplash.com/photo-1586495777744-4413f21062fa?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8bGlwc3RpY2t8ZW58MHx8MHx8fDA%3D&auto=format&fit=crop&w=500&q=60",

        
    },
    {
      
        "name": "Pro Foundation Palette",
        "category": "makeup",
        "price": 45.99,
        "rating": 4.5,
        "reviews": 156,
        "description": "Full coverage foundation palette with 12 shades for all skin tones.",
        "image": "https://images.unsplash.com/photo-1596462502278-27bfdc403348?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8Zm91bmRhdGlvbnxlbnwwfHwwfHx8MA%3D%3D&auto=format&fit=crop&w=500&q=60",

        
    },
    {
       
        "name": "Eyeshadow Master Palette",
        "category": "makeup",
        "price": 52.99,
        "rating": 4.8,
        "reviews": 324,
        "description": "Professional eyeshadow palette with 24 highly pigmented matte and shimmer shades.",
        "image": "https://images.unsplash.com/photo-1547934659-7fa699ef3ce0?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",

       
    },
    {
       
        "name": "Luxury Mascara",
        "category": "makeup",
        "price": 28.99,
        "rating": 4.6,
        "reviews": 198,
        "description": "Volumizing mascara for dramatic lashes, waterproof and smudge-proof.",
        "image": "https://images.unsplash.com/photo-1623071280399-238e1f181fa6?q=80&w=735&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",

  
    },
    {
       
        "name": "Gel Nail Polish Set",
        "category": "nail-polish",
        "price": 29.99,
        "rating": 4.4,
        "reviews": 167,
        "description": "12-piece gel nail polish set with glossy finish and long-lasting wear.",
        "image": "https://plus.unsplash.com/premium_photo-1670338554262-69ef494b540c?q=80&w=686&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8bmFpbCUyMHBvbGlzaHxlbnwwfHwwfHx8MA%3D%3D&auto=format&fit=crop&w=500&q=60",

       
    },
    {
        
        "name": "Metallic Nail Lacquer",
        "category": "nail-polish",
        "price": 12.99,
        "rating": 4.3,
        "reviews": 89,
        "description": "Shimmering metallic nail polish with quick-dry formula in 8 stunning shades.",
        "image": "https://images.unsplash.com/photo-1599948128020-9a44505b0d1b?q=80&w=687&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",

   
    },
    {
     
        "name": "Designer Silk Dress",
        "category": "clothing",
        "price": 189.99,
        "rating": 4.7,
        "reviews": 234,
        "description": "Elegant silk evening dress with intricate embroidery and flowing silhouette.",
        "image": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8ZHJlc3N8ZW58MHx8MHx8fDA%3D&auto=format&fit=crop&w=500&q=60",

      
    },
    {
        
        "name": "Premium Denim Jeans",
        "category": "clothing",
        "price": 89.99,
        "rating": 4.5,
        "reviews": 312,
        "description": "High-quality denim jeans with perfect fit and comfortable stretch fabric.",
        "image": "https://images.unsplash.com/photo-1542272604-787c3835535d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8amVhbnN8ZW58MHx8MHx8fDA%3D%3D&auto=format&fit=crop&w=500&q=60",
     
    },
    {
        
        "name": "Cashmere Sweater",
        "category": "clothing",
        "price": 149.99,
        "rating": 4.8,
        "reviews": 178,
        "description": "Luxurious cashmere sweater for ultimate comfort and warmth in winter.",
        "image": "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8c3dlYXRlcnxlbnwwfHwwfHx8MA%3D%3D&auto=format&fit=crop&w=500&q=60",
      
      
    },
    {
      
        "name": "Linen Summer Shirt",
        "category": "clothing",
        "price": 65.99,
        "rating": 4.4,
        "reviews": 145,
        "description": "Breathable linen shirt perfect for summer, available in multiple colors.",
        "image": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8c2hpcnR8ZW58MHx8MHx8fDA%3D%3D&auto=format&fit=crop&w=500&q=60",
     
        
    },
    {
        
        "name": "Leather Ankle Boots",
        "category": "shoes",
        "price": 129.99,
        "rating": 4.6,
        "reviews": 267,
        "description": "Genuine leather ankle boots with comfortable cushioning and stylish design.",
        "image": "https://images.unsplash.com/photo-1542280756-74b2f55e73ab?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8Ym9vdHN8ZW58MHx8MHx8fDA%3D%3D&auto=format&fit=crop&w=500&q=60",
       
 
    },
    {
       
        "name": "Running Sneakers",
        "category": "shoes",
        "price": 99.99,
        "rating": 4.7,
        "reviews": 423,
        "description": "Lightweight running sneakers with advanced cushioning technology.",
        "image": "https://images.unsplash.com/photo-1549298916-b41d501d3772?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8c25lYWtlcnN8ZW58MHx8MHx8fDA%3D%3D&auto=format&fit=crop&w=500&q=60",

   
    },
    {
      
        "name": "Elegant High Heels",
        "category": "shoes",
        "price": 79.99,
        "rating": 4.3,
        "reviews": 189,
        "description": "Classic high heels for formal occasions, available in various colors.",
        "image": "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8aGVlbHN8ZW58MHx8MHx8fDA%3D%3D&auto=format&fit=crop&w=500&q=60",

    
    },
    {
        
        "name": "Comfort Sandals",
        "category": "shoes",
        "price": 45.99,
        "rating": 4.2,
        "reviews": 156,
        "description": "Comfortable summer sandals with arch support and adjustable straps.",
        "image": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8c2FuZGFsc3xlbnwwfHwwfHx8MA%3D%3D&auto=format&fit=crop&w=500&q=60",
        "store": {
            "id": 3,
            "name": "Fashion Hub",
            "rating": 4.5,
            "products": 267
        },
    
    },
    {
       
        "name": "Designer Leather Handbag",
        "category": "bags",
        "price": 299.99,
        "rating": 4.8,
        "reviews": 198,
        "description": "Luxury leather handbag with multiple compartments and gold-tone hardware.",
        "image": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8aGFuZGJhZ3xlbnwwfHwwfHx8MA%3D%3D&auto=format&fit=crop&w=500&q=60",
        "store": {
            "id": 3,
            "name": "Fashion Hub",
            "rating": 4.5,
            "products": 267
        },
      
    },
    {
       
        "name": "Canvas Backpack",
        "category": "bags",
        "price": 59.99,
        "rating": 4.5,
        "reviews": 267,
        "description": "Durable canvas backpack with laptop compartment and water-resistant material.",
        "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8YmFja3BhY2t8ZW58MHx8MHx8fDA%3D%3D&auto=format&fit=crop&w=500&q=60",

     
    },
    {
        
        "name": "Evening Clutch",
        "category": "bags",
        "price": 89.99,
        "rating": 4.4,
        "reviews": 134,
        "description": "Elegant evening clutch with sequin detailing and detachable chain strap.",
        "image": "https://images.unsplash.com/photo-1591561954557-26941169b49e?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8Y2x1dGNofGVufDB8fDB8fHww&auto=format&fit=crop&w=500&q=60",


    },
    
    {
       
        "name": "Gold Chain Necklace",
        "category": "jewelry",
        "price": 189.99,
        "rating": 4.6,
        "reviews": 223,
        "description": "Elegant gold chain necklace with adjustable length and secure clasp.",
        "image": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8bmVja2xhY2V8ZW58MHx8MHx8fDA%3D%3D&auto=format&fit=crop&w=500&q=60",

    },
    {
       
        "name": "Silver Bracelet Set",
        "category": "jewelry",
        "price": 79.99,
        "rating": 4.5,
        "reviews": 178,
        "description": "Sterling silver bracelet set with delicate charms and adjustable sizing.",
        "image": "https://plus.unsplash.com/premium_photo-1709033404514-c3953af680b4?q=80&w=687&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",

      
    },
    {
        
        "name": "Pearl Drop Earrings",
        "category": "jewelry",
        "price": 129.99,
        "rating": 4.7,
        "reviews": 145,
        "description": "Elegant pearl drop earrings with gold accents, perfect for special occasions.",
        "image": "https://images.unsplash.com/photo-1665198134143-8c4434d3578b?q=80&w=635&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",

        
    },
    {
        "name": "Rose Gold Ring Set",
        "category": "jewelry",
        "price": 149.99,
        "rating": 4.4,
        "reviews": 167,
        "description": "Stackable rose gold rings with delicate gemstone accents.",
        "image": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8cmluZ3N8ZW58MHx8MHx8fDA%3D%3D&auto=format&fit=crop&w=500&q=60",

      
    },
        {
        "name": "Sweater",
        "category": "jewelry",
        "price": 149.99,
        "rating": 4.4,
        "reviews": 167,
        "description": "Stackable rose gold rings with delicate gemstone accents.",
        "image": "https://images.unsplash.com/photo-1601379327928-bedfaf9da2d0?q=80&w=687&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",

      
    },
    {
        "name": "Nivea Lip Balm",
        "category": "makeup",
        "price": 149.99,
        "rating": 4.4,
        "reviews": 167,
        "description": "Nivea lip balm with moisturizing formula for soft and smooth lips.",
        "image": "https://images.unsplash.com/photo-1752327091564-c177af1f971c?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",

      
    },
        {
        "name": "St london lipstick",
        "category": "makeup",
        "price": 149.99,
        "rating": 4.4,
        "reviews": 167,
        "description": "St london lipstick with moisturizing formula for soft and smooth lips.",
        "image": "https://luxuronline.com/wp-content/uploads/2024/06/ST-London-Velvet-Ultra-Matt-Lipstick-Hyper-Brown-Luxur-1200x1371.jpg",

      
    }
    ]
    
    with app.app_context():
        db = SessionLocal()
        
        try:
            factory_manager = ProductFactoryManager()
            added_count = 0
            
            for product_data in products_data:
                # Check if product already exists (by name or other unique identifier)
                existing_product = db.query(Product).filter(
                    Product.name == product_data['name']
                ).first()
                
                # If product doesn't exist, create it
                if not existing_product:
                    factory = factory_manager.get_factory(product_data['category'])
                    builder = ProductBuilder(factory)
                    
                    if product_data['category'] in ['makeup', 'nail-polish']:
                        builder.set_subcategory(product_data['category'])
                    
                    product = (builder
                              .set_name(product_data['name'])
                              .set_price(product_data['price'])
                              .set_description(product_data['description'])
                              .set_image(product_data['image'])
                              .set_rating(product_data['rating'])
                              .set_reviews(product_data['reviews'])
                              .build())
                    
                    db.add(product)
                    added_count += 1
                    print(f"➕ Added: {product_data['name']}")
                else:
                    print(f"⏭️ Skipped (already exists): {product_data['name']}")
            
            db.commit()
            print(f"\n✅ Successfully added {added_count} new products")
            print(f"⏭️ Skipped {len(products_data) - added_count} existing products")
            print(f"📊 Total products in database now: {db.query(Product).count()}")
        
        except Exception as e:
            db.rollback()
            print(f"❌ Error seeding database: {e}")
        
        finally:
            db.close()

if __name__ == '__main__':
    seed_products()