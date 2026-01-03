from abc import ABC, abstractmethod
from models import Product
from typing import Dict, Any

# Abstract Factory
class ProductFactory(ABC):
    @abstractmethod
    def create_product(self, data: Dict[str, Any]) -> Product:
        pass
    
    @abstractmethod
    def get_product_type(self) -> str:
        pass
    
    @abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> bool:
        pass

# Concrete Factories for each product category
class ElectronicsFactory(ProductFactory):
    def create_product(self, data: Dict[str, Any]) -> Product:
        return Product(
            name=data['name'],
            category='electronics',
            price=data['price'],
            rating=data.get('rating', 0.0),
            reviews=data.get('reviews', 0),
            description=data['description'],
            image=data['image']
        )
    
    def get_product_type(self) -> str:
        return 'electronics'
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        required = ['name', 'price', 'description', 'image']
        return all(key in data for key in required)

class AudioFactory(ProductFactory):
    def create_product(self, data: Dict[str, Any]) -> Product:
        return Product(
            name=data['name'],
            category='audio',
            price=data['price'],
            rating=data.get('rating', 0.0),
            reviews=data.get('reviews', 0),
            description=data['description'],
            image=data['image']
        )
    
    def get_product_type(self) -> str:
        return 'audio'
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        required = ['name', 'price', 'description', 'image']
        return all(key in data for key in required)

class ClothingFactory(ProductFactory):
    def create_product(self, data: Dict[str, Any]) -> Product:
        return Product(
            name=data['name'],
            category='clothing',
            price=data['price'],
            rating=data.get('rating', 0.0),
            reviews=data.get('reviews', 0),
            description=data['description'],
            image=data['image']
        )
    
    def get_product_type(self) -> str:
        return 'clothing'
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        required = ['name', 'price', 'description', 'image']
        return all(key in data for key in required)

class BeautyFactory(ProductFactory):
    def create_product(self, data: Dict[str, Any]) -> Product:
        category = data.get('subcategory', 'makeup')
        return Product(
            name=data['name'],
            category=category,
            price=data['price'],
            rating=data.get('rating', 0.0),
            reviews=data.get('reviews', 0),
            description=data['description'],
            image=data['image']
        )
    
    def get_product_type(self) -> str:
        return 'beauty'
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        required = ['name', 'price', 'description', 'image']
        return all(key in data for key in required)

class JewelryFactory(ProductFactory):
    def create_product(self, data: Dict[str, Any]) -> Product:
        return Product(
            name=data['name'],
            category='jewelry',
            price=data['price'],
            rating=data.get('rating', 0.0),
            reviews=data.get('reviews', 0),
            description=data['description'],
            image=data['image']
        )
    
    def get_product_type(self) -> str:
        return 'jewelry'
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        required = ['name', 'price', 'description', 'image']
        return all(key in data for key in required)

# Factory Manager (Singleton Pattern)
class ProductFactoryManager:
    _instance = None
    _factories = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProductFactoryManager, cls).__new__(cls)
            cls._instance._initialize_factories()
        return cls._instance
    
    def _initialize_factories(self):
        self._factories = {
            'electronics': ElectronicsFactory(),
            'audio': AudioFactory(),
            'wearables': ElectronicsFactory(),
            'photography': ElectronicsFactory(),
            'mobile': ElectronicsFactory(),
            'gaming': ElectronicsFactory(),
            'clothing': ClothingFactory(),
            'shoes': ClothingFactory(),
            'bags': ClothingFactory(),
            'jewelry': JewelryFactory(),
            'makeup': BeautyFactory(),
            'nail-polish': BeautyFactory()
            
        }
    
    def get_factory(self, product_type: str) -> ProductFactory:
        factory = self._factories.get(product_type.lower())
        if not factory:
            raise ValueError(f"No factory found for product type: {product_type}")
        return factory
    
    def get_all_factories(self):
        return self._factories

# Product Builder (Builder Pattern)
class ProductBuilder:
    def __init__(self, factory: ProductFactory):
        self.factory = factory
        self.product_data = {}
    
    def set_name(self, name: str):
        self.product_data['name'] = name
        return self
    
    def set_price(self, price: float):
        self.product_data['price'] = price
        return self
    
    def set_description(self, description: str):
        self.product_data['description'] = description
        return self
    
    def set_image(self, image: str):
        self.product_data['image'] = image
        return self
    
    def set_rating(self, rating: float):
        self.product_data['rating'] = rating
        return self
    
    def set_reviews(self, reviews: int):
        self.product_data['reviews'] = reviews
        return self
    
    def set_subcategory(self, subcategory: str):
        self.product_data['subcategory'] = subcategory
        return self
    
    def build(self) -> Product:
        if not self.factory.validate_data(self.product_data):
            raise ValueError("Invalid product data for factory")
        return self.factory.create_product(self.product_data)